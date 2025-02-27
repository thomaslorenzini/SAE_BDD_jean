#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                        template_folder='templates')


# validation de la commande : partie 2 -- vue pour choisir les adresses (livraision et facturation)
@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = """
    SELECT 
        j.id_jean AS id_article,
        j.nom_jean AS nom,
        j.prix_jean AS prix,
        lp.quantite_panier AS quantite
    FROM ligne_panier lp
    JOIN jean j ON lp.id_jean = j.id_jean
    WHERE lp.id_utilisateur = %s
    """
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()
    if len(articles_panier) >= 1:
        sql_total = """
                SELECT SUM(j.prix_jean * lp.quantite_panier) AS total
                FROM ligne_panier lp
                JOIN jean j ON lp.id_jean = j.id_jean
                WHERE lp.id_utilisateur = %s
            """
        mycursor.execute(sql_total, (id_client,))
        result_total = mycursor.fetchone()
        prix_total = result_total['total']
    else:
        prix_total = None
    # etape 2 : selection des adresses
    sql_adresse = "SELECT * FROM adresse WHERE id_utilisateur = %s"
    mycursor.execute(sql_adresse, (id_client,))
    adresses = mycursor.fetchall()
    return render_template('client/boutique/panier_validation_adresses.html'
                           , adresses=adresses
                           , articles_panier=articles_panier
                           , prix_total= prix_total
                           , validation=1
                           #, id_adresse_fav=id_adresse_fav
                           )


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()

    # choix de(s) (l')adresse(s)

    id_client = session['id_user']
    id_adresse_livraison = request.form.get('id_adresse_livraison')
    id_adresse_facturation = request.form.get('id_adresse_facturation')
    if request.form.get('adresse_identique') == 'adresse_identique':
        id_adresse_facturation = id_adresse_livraison

    sql_panier = """
        SELECT 
            j.id_jean AS id_article,
            j.nom_jean AS nom,
            j.prix_jean AS prix,
            lp.quantite_panier AS quantite
        FROM ligne_panier lp
        JOIN jean j ON lp.id_jean = j.id_jean
        WHERE lp.id_utilisateur = %s
        """
    mycursor.execute(sql_panier, (id_client,))
    items_ligne_panier = mycursor.fetchall()

    if items_ligne_panier is None or len(items_ligne_panier) < 1:
         flash(u'Pas d\'articles dans le ligne_panier', 'alert-warning')
         return redirect('/client/article/show')
                                           # https://pynative.com/python-mysql-transaction-management-using-commit-rollback/
    date_achat = datetime.strptime(str(datetime.now().date().strftime("%b %d %Y %H:%M")), "%b %d %Y %H:%M")
    id_etat = 1

    sql_insert_commande = """
        INSERT INTO commande (date_achat, id_etat, id_utilisateur, id_adresse_livraison, id_adresse_facturation)
        VALUES (%s, %s, %s, %s, %s)
        """
    mycursor.execute(sql_insert_commande, (date_achat, id_etat, id_client, id_adresse_livraison, id_adresse_facturation))
    commande_id = mycursor.lastrowid # doc mysql

    sql = '''SELECT last_insert_id() as last_insert_id'''
    # numéro de la dernière commande

    for item in items_ligne_panier:
        sql_insert_ligne_commande = """
                INSERT INTO ligne_commande (id_commande, id_jean, prix, quantite_commande)
                VALUES (%s, %s, %s, %s)
                """
        mycursor.execute(sql_insert_ligne_commande, (commande_id, item['id_article'], item['prix'], item['quantite']))
    sql_delete_panier = "DELETE FROM ligne_panier WHERE id_utilisateur = %s"
    mycursor.execute(sql_delete_panier, (id_client,))
    get_db().commit()
    flash(u'Commande ajoutée','alert-success')
    return redirect('/client/article/show')




@client_commande.route('/client/commande/show', methods=['get','post'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql_commandes = """
            SELECT c.id_commande,
                   c.date_achat,
                   c.id_etat,
                   e.libelle,
                   (SELECT COUNT(*) FROM ligne_commande lc WHERE lc.id_commande = c.id_commande) AS nbr_articles,
                   (SELECT SUM(lc.prix * lc.quantite_commande) FROM ligne_commande lc WHERE lc.id_commande = c.id_commande) AS prix_total
            FROM commande c
            JOIN etat e ON c.id_etat = e.id_etat
            WHERE c.id_utilisateur = %s
            ORDER BY c.id_etat, c.date_achat DESC
        """
    mycursor.execute(sql_commandes, (id_client,))
    commandes = mycursor.fetchall()

    articles_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    if id_commande != None:
        print(id_commande)
        sql_articles = """
                    SELECT j.nom_jean AS nom,
                           lc.quantite_commande AS quantite,
                           lc.prix AS prix,
                           (lc.quantite_commande * lc.prix) AS prix_ligne,
                           1 AS nb_declinaisons,
                           1 AS couleur_id,
                           '' AS libelle_couleur,
                           1 AS taille_id,
                           '' AS libelle_taille
                    FROM ligne_commande lc
                    JOIN jean j ON lc.id_jean = j.id_jean
                    WHERE lc.id_commande = %s
                """
        mycursor.execute(sql_articles, (id_commande,))
        articles_commande = mycursor.fetchall()

        sql_adresses = """
                    SELECT 
                        a_liv.nom AS nom_livraison,
                        a_liv.rue AS rue_livraison,
                        a_liv.code_postal AS code_postal_livraison,
                        a_liv.ville AS ville_livraison,
                        a_fact.nom AS nom_facturation,
                        a_fact.rue AS rue_facturation,
                        a_fact.code_postal AS code_postal_facturation,
                        a_fact.ville AS ville_facturation,
                        CASE WHEN c.id_adresse_livraison = c.id_adresse_facturation THEN 'adresse_identique' ELSE 'different' END AS adresse_identique
                    FROM commande c
                    JOIN adresse a_liv ON c.id_adresse_livraison = a_liv.id_adresse
                    JOIN adresse a_fact ON c.id_adresse_facturation = a_fact.id_adresse
                    WHERE c.id_commande = %s
                """
        mycursor.execute(sql_adresses, (id_commande,))
        commande_adresses = mycursor.fetchone()

    return render_template('client/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           , commande_adresses=commande_adresses
                           )


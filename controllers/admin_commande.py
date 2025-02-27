#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                        template_folder='templates')

@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')


@admin_commande.route('/admin/commande/show', methods=['get','post'])
def admin_commande_show():
    mycursor = get_db().cursor()
    admin_id = session['id_user']
    sql_commandes = """
        SELECT c.id_commande,
               c.date_achat,
               c.id_etat,
               u.login,
               e.libelle,
               (SELECT COUNT(*) FROM ligne_commande lc WHERE lc.id_commande = c.id_commande) AS nbr_articles,
               (SELECT SUM(lc.prix * lc.quantite_commande) FROM ligne_commande lc WHERE lc.id_commande = c.id_commande) AS prix_total
        FROM commande c
        JOIN etat e ON c.id_etat = e.id_etat
        JOIN utilisateur u ON c.id_utilisateur = u.id_utilisateur
        ORDER BY c.id_etat, c.date_achat DESC
        """
    mycursor.execute(sql_commandes)
    commandes = mycursor.fetchall()

    articles_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    print(id_commande)
    if id_commande != None:
        sql_articles = """
                    SELECT j.nom_jean AS nom,
                           lc.quantite_commande AS quantite,
                           lc.prix AS prix,
                           (lc.quantite_commande * lc.prix) AS prix_ligne,
                           1 AS nb_declinaisons,
                           1 AS couleur_id,
                           '' AS libelle_couleur,
                           1 AS taille_id,
                           '' AS libelle_taille,
                           c.id_etat AS etat_id,
                           c.id_commande AS id
                    FROM ligne_commande lc
                    JOIN jean j ON lc.id_jean = j.id_jean
                    JOIN commande c ON lc.id_commande = c.id_commande
                    WHERE lc.id_commande = %s
                """
        mycursor.execute(sql_articles, (id_commande,))
        articles_commande = mycursor.fetchall()

        sql_adresses = """
                   SELECT 
                       al.nom AS nom_livraison,
                       al.rue AS rue_livraison,
                       al.code_postal AS code_postal_livraison,
                       al.ville AS ville_livraison,
                       af.nom AS nom_facturation,
                       af.rue AS rue_facturation,
                       af.code_postal AS code_postal_facturation,
                       af.ville AS ville_facturation,
                       CASE 
                           WHEN c.id_adresse_livraison = c.id_adresse_facturation THEN 'adresse_identique' 
                           ELSE 'different' 
                       END AS adresse_identique
                   FROM commande c
                   LEFT JOIN adresse al ON c.id_adresse_livraison = al.id_adresse
                   LEFT JOIN adresse af ON c.id_adresse_facturation = af.id_adresse
                   WHERE c.id_commande = %s
                """
        mycursor.execute(sql_adresses, (id_commande,))
        commande_adresses = mycursor.fetchone()
    return render_template('admin/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           , commande_adresses=commande_adresses
                           )


@admin_commande.route('/admin/commande/valider', methods=['get','post'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    if commande_id != None:
        print(commande_id)
        sql = "UPDATE commande SET id_etat = 2 WHERE id_commande = %s"
        mycursor.execute(sql, (commande_id,))
        get_db().commit()
    return redirect('/admin/commande/show')

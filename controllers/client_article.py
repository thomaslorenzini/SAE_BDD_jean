#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_article = Blueprint('client_article', __name__,
                        template_folder='templates')

@client_article.route('/client/index')
@client_article.route('/client/article/show')              # remplace /client
def client_article_show():                                 # remplace client_index
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''
        SELECT 
            a.id_jean AS id_article,
            a.nom_jean AS nom,
            a.prix_jean AS prix,
            a.image AS image,
            a.stock AS stock,
            a.couleur AS couleur,
            a.descripton AS description,
            a.fournisseur AS fournisseur,
            a.marque AS marque,
            t.nom_taille AS type_article_id,
            c.nom_coupe AS coupe,
            (SELECT COUNT(*) FROM ligne_panier lp WHERE lp.id_jean = a.id_jean) AS nb_panier,  
            (SELECT COUNT(*) FROM ligne_commande lc WHERE lc.id_jean = a.id_jean) AS nb_commandes,
            (SELECT COUNT(*) FROM ligne_commande lc WHERE lc.id_jean = a.id_jean AND lc.quantite_commande > 0) AS nb_commandes_valides 
        FROM jean a
        JOIN taille t ON a.id_taille = t.id_taille
        JOIN coupe_jean c ON a.id_coupe_jean = c.id_coupe_jean
    '''

    params = []

    if session.get('filter_word'):
        sql += " AND (a.nom_jean LIKE %s OR a.descripton LIKE %s OR a.couleur LIKE %s)"
        mot = "%" + session['filter_word'] + "%"
        params.extend([mot, mot, mot])

    if session.get('filter_prix_min'):
        sql += " AND a.prix_jean >= %s"
        params.append(session['filter_prix_min'])

    if session.get('filter_prix_max'):
        sql += " AND a.prix_jean <= %s"
        params.append(session['filter_prix_max'])

    if session.get('filter_types'):
        types = session['filter_types']
        sql += " AND a.id_coupe_jean IN (" + ", ".join(["%s"] * len(types)) + ")"
        params.extend(types)

    if session.get('filter_tailles'):
        tailles = session['filter_tailles']
        sql += " AND a.id_taille IN (" + ", ".join(["%s"] * len(tailles)) + ")"
        params.extend(tailles)

    sql += " ORDER BY a.id_jean ASC;"

    mycursor.execute(sql, params)
    articles = mycursor.fetchall()

    mycursor.execute("SELECT * FROM coupe_jean")
    types_article = mycursor.fetchall()

    mycursor.execute("SELECT * FROM taille")
    items_taille = mycursor.fetchall()

    sql_panier = """
           SELECT 
               j.id_jean AS id_article,
               j.nom_jean AS nom,
               j.prix_jean AS prix,
               lp.quantite_panier AS quantite,
               j.stock,
               1 AS id_declinaison_article,
               j.couleur AS libelle_couleur,
               t.nom_taille AS libelle_taille,
               j.id_taille AS id_taille
           FROM ligne_panier lp
           JOIN jean j ON lp.id_jean = j.id_jean
           LEFT JOIN taille t ON j.id_taille = t.id_taille
           WHERE lp.id_utilisateur = %s
       """
    mycursor.execute(sql_panier, (id_client,))
    articles_panier = mycursor.fetchall()

    if articles_panier:
        sql_total = """
                SELECT SUM(j.prix_jean * lp.quantite_panier) AS total
                FROM ligne_panier lp
                JOIN jean j ON lp.id_jean = j.id_jean
                WHERE lp.id_utilisateur = %s
            """
        mycursor.execute(sql_total, (id_client,))


    if len(articles_panier) >= 1:
        sql = ''' calcul du prix total du panier '''
        prix_total = None
    else:
        prix_total = None
    return render_template('client/boutique/panier_article.html'
                           , articles=articles
                           , articles_panier=articles_panier
                           #, prix_total=prix_total
                           , items_filtre=types_article
                           , items_taille=items_taille
                           )

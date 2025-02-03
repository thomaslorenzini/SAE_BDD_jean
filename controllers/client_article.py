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
                ORDER BY a.id_jean ASC; 
            '''
    list_param = []
    condition_and = ""
    # utilisation du filtre
    sql3=''' prise en compte des commentaires et des notes dans le SQL    '''




    articles =[]
    mycursor.execute(sql)
    articles = mycursor.fetchall()


    # pour le filtre
    types_article = []



    mycursor.execute("SELECT * FROM coupe_jean")
    types_article = mycursor.fetchall()

    # ---- Nouveau bloc pour récupérer les tailles ----
    mycursor.execute("SELECT * FROM taille")
    items_taille = mycursor.fetchall()


    articles_panier = []

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

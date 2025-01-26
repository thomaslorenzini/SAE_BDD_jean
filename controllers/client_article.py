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
            a.id_jean AS article_id,
            a.nom_jean AS nom,
            a.prix_jean AS prix,
            a.image AS image,
            a.matiere AS matiere,
            a.couleur AS couleur,
            a.descripton AS description,
            a.fournisseur AS fournisseur,
            a.marque AS marque,
            t.nom_taille AS taille,
            c.nom_coupe AS coupe,
            e.libelle AS etat
        FROM jean a
        JOIN taille t ON a.id_taille = t.id_taille
        JOIN coupe_jean c ON a.id_coupe_jean = c.id_coupe_jean
        JOIN ligne_commande lc ON a.id_jean = lc.id_jean
        JOIN commande cmd ON lc.id_commande = cmd.id_commande
        JOIN etat e ON cmd.id_etat = e.id_etat
        WHERE cmd.id_utilisateur = %s
        '''
    list_param = []
    condition_and = ""
    # utilisation du filtre
    sql3=''' prise en compte des commentaires et des notes dans le SQL    '''
    articles =[]
    mycursor.execute(sql, (id_client,))  # Exécution de la requête avec l'ID utilisateur
    articles = mycursor.fetchall()


    # pour le filtre
    types_article = []


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
                           )

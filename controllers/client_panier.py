#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                        template_folder='templates')


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    quantite = request.form.get('quantite')
    # ---------
    #id_declinaison_article=request.form.get('id_declinaison_article',None)
    #id_declinaison_article = 1

# ajout dans le panier d'une déclinaison d'un article (si 1 declinaison : immédiat sinon => vu pour faire un choix
    # sql = '''    '''
    # mycursor.execute(sql, (id_article))
    # declinaisons = mycursor.fetchall()
    # if len(declinaisons) == 1:
    #     id_declinaison_article = declinaisons[0]['id_declinaison_article']
    # elif len(declinaisons) == 0:
    #     abort("pb nb de declinaison")
    # else:
    #     sql = '''   '''
    #     mycursor.execute(sql, (id_article))
    #     article = mycursor.fetchone()
    #     return render_template('client/boutique/declinaison_article.html'
    #                                , declinaisons=declinaisons
    #                                , quantite=quantite
    #                                , article=article)

# ajout dans le panier d'un article
    quantite = int(quantite)
    sql = "SELECT stock FROM jean WHERE id_jean = %s"
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()
    if article is None or article['stock'] < quantite:
        abort(400, "Stock insuffisant ou article introuvable")

    # Vérification si l'article est déjà présent dans le panier
    sql = "SELECT quantite_panier FROM ligne_panier WHERE id_utilisateur = %s AND id_jean = %s"
    mycursor.execute(sql, (id_client, id_article))
    ligne = mycursor.fetchone()

    if ligne is not None:
        sql = ("UPDATE ligne_panier SET quantite_panier = quantite_panier + %s, "
               "date_ajout = CURDATE() WHERE id_utilisateur = %s AND id_jean = %s")
        mycursor.execute(sql, (quantite, id_client, id_article))
    else:
        sql = ("INSERT INTO ligne_panier (id_utilisateur, id_jean, quantite_panier, date_ajout) "
               "VALUES (%s, %s, %s, CURDATE())")
        mycursor.execute(sql, (id_client, id_article, quantite))

    sql = "UPDATE jean SET stock = stock - %s WHERE id_jean = %s"
    mycursor.execute(sql, (quantite, id_article))

    get_db().commit()


    return redirect('/client/article/show')

@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article','')
    quantite = 1

    # ---------
    # partie 2 : on supprime une déclinaison de l'article
    # id_declinaison_article = request.form.get('id_declinaison_article', None)

    sql = "SELECT quantite_panier FROM ligne_panier WHERE id_utilisateur = %s AND id_jean = %s"
    mycursor.execute(sql, (id_client, id_article))
    article_panier = mycursor.fetchone()

    if article_panier and article_panier['quantite_panier'] > 1:
        sql = "UPDATE ligne_panier SET quantite_panier = quantite_panier - 1 WHERE id_utilisateur = %s AND id_jean = %s"
        mycursor.execute(sql, (id_client, id_article))
    else:
        sql = "DELETE FROM ligne_panier WHERE id_utilisateur = %s AND id_jean = %s"
        mycursor.execute(sql, (id_client, id_article))

    sql = "UPDATE jean SET stock = stock + 1 WHERE id_jean = %s"
    mycursor.execute(sql, (id_article,))
    get_db().commit()
    return redirect('/client/article/show')





@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']
    sql = "SELECT id_jean, quantite_panier FROM ligne_panier WHERE id_utilisateur = %s"
    mycursor.execute(sql, (client_id,))
    items_panier = mycursor.fetchall()
    for item in items_panier:
        id_article = item['id_jean']
        quantite = item['quantite_panier']

        sql_delete = "DELETE FROM ligne_panier WHERE id_utilisateur = %s AND id_jean = %s"
        mycursor.execute(sql_delete, (client_id, id_article))

        sql_update = "UPDATE jean SET stock = stock + %s WHERE id_jean = %s"
        mycursor.execute(sql_update, (quantite, id_article))
        get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    #id_declinaison_article = request.form.get('id_declinaison_article')

    sql_select = "SELECT quantite_panier FROM ligne_panier WHERE id_utilisateur = %s AND id_jean = %s"
    mycursor.execute(sql_select, (id_client, id_article))
    ligne = mycursor.fetchone()

    quantite_line = ligne['quantite_panier']
    sql_delete = "DELETE FROM ligne_panier WHERE id_utilisateur = %s AND id_jean = %s"
    mycursor.execute(sql_delete, (id_client, id_article))

    sql_update_stock = "UPDATE jean SET stock = stock + %s WHERE id_jean = %s"
    mycursor.execute(sql_update_stock, (quantite_line, id_article))

    get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    filter_word = request.form.get('filter_word', None)
    filter_prix_min = request.form.get('filter_prix_min', None)
    filter_prix_max = request.form.get('filter_prix_max', None)
    filter_types = request.form.getlist('filter_types', None)
    filter_tailles = request.form.getlist('filter_tailles', None)
    # test des variables puis
    # mise en session des variables

    session['filter_word'] = filter_word
    session['filter_prix_min'] = filter_prix_min
    session['filter_prix_max'] = filter_prix_max
    session['filter_types'] = filter_types
    session['filter_tailles'] = filter_tailles

    return redirect('/client/article/show')


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    # suppression  des variables en session
    session.pop('filter_word', None)
    session.pop('filter_types', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    session.pop('filter_tailles', None)

    print("suppr filtre")
    return redirect('/client/article/show')

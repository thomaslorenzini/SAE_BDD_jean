#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, Flask, request, render_template, redirect, url_for, abort, flash, session, g
from connexion_db import get_db
from controllers.client_liste_envies import client_historique_add

client_commentaire = Blueprint('client_commentaire', __name__,
                               template_folder='templates')

#------------DETAILS ARTICLE -------------------------
@client_commentaire.route('/client/article/details', methods=['GET'])
def client_article_details():
    mycursor = get_db().cursor()

    id_article = request.args.get('id_article', None)
    id_client = session['id_user']

    if not id_article:
        abort(400, "ID article manquant")


#-----------------NB NOTES ET MOYENNE NOTES----------------------
    sql_article = '''
        SELECT
            id_jean AS id_article,
            nom_jean AS nom,
            descripton AS description,
            prix_jean AS prix,
            image,
            (SELECT AVG(note) FROM notes WHERE article_id = %s) AS moyenne_notes,
            (SELECT COUNT(*) FROM notes WHERE article_id = %s) AS nb_notes
        FROM jean
        WHERE id_jean = %s
    '''
    mycursor.execute(sql_article, (id_article, id_article, id_article))
    article = mycursor.fetchone()
    if article is None:
        abort(404, "Article non trouvé")


    sql_commandes_articles = '''
        SELECT COUNT(*) AS nb_commandes_article
        FROM ligne_commande
        WHERE id_jean = %s
          AND id_commande IN (
              SELECT id_commande FROM commande WHERE id_utilisateur = %s
          )
    '''
    mycursor.execute(sql_commandes_articles, (id_article, id_client))
    commandes_articles = mycursor.fetchone()

    # ------------TROUVER NOTE DE UTILISATEUR -------------------------
    sql_note = '''
        SELECT note FROM notes
        WHERE id_utilisateur = %s AND article_id = %s
    '''
    mycursor.execute(sql_note, (id_client, id_article))
    note_record = mycursor.fetchone()
    note = note_record['note'] if note_record else None



    # ------------LES COMMENTAIRES-------------------------

    # ------------COMPTER COMMS  -------------------------
    sql_nb_commentaires = '''
        SELECT
            (SELECT COUNT(*) FROM commentaires WHERE article_id = %s) AS nb_commentaires_total,
            (SELECT COUNT(*) FROM commentaires WHERE article_id = %s AND id_utilisateur = %s) AS nb_commentaires_utilisateur,
            (SELECT COUNT(*) FROM commentaires WHERE article_id = %s AND valide = 1) AS nb_commentaires_total_valide,
            (SELECT COUNT(*) FROM commentaires WHERE article_id = %s AND id_utilisateur = %s AND valide = 1) AS nb_commentaires_utilisateur_valide
    '''
    mycursor.execute(sql_nb_commentaires, (id_article, id_article, id_client, id_article, id_article, id_client))
    nb_commentaires = mycursor.fetchone()

    # ------------LISTE DES COMMS -------------------------
    sql_commentaires = '''
        SELECT c.id AS id_commentaire, c.commentaire, c.date_publication, u.login, c.id_utilisateur
        FROM commentaires c
        JOIN utilisateur u ON c.id_utilisateur = u.id_utilisateur
        WHERE c.article_id = %s
        ORDER BY c.date_publication DESC
    '''
    mycursor.execute(sql_commentaires, (id_article,))
    commentaires = mycursor.fetchall()

    return render_template('client/article_info/article_details.html',
                           article=article,
                           commandes_articles=commandes_articles,
                           note=note,
                           nb_commentaires=nb_commentaires,
                           commentaires=commentaires)



#------------AJOUTER COMM -------------------------------
@client_commentaire.route('/client/commentaire/add', methods=['POST'])
def client_comment_add():
    mycursor = get_db().cursor()
    commentaire = request.form.get('commentaire', None)
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)

    if commentaire == '':
        flash(u'Commentaire vide', 'warning')
        return redirect('/client/article/details?id_article=' + id_article)

    # Vérifier le nombre de commentaires déjà postés par cet utilisateur sur cet article
    sql_nb_commentaires = '''
        SELECT COUNT(*) AS nb_commentaires_utilisateur
        FROM commentaires
        WHERE article_id = %s AND id_utilisateur = %s
    '''
    mycursor.execute(sql_nb_commentaires, (id_article, id_client))
    result = mycursor.fetchone()
    nb_commentaires_utilisateur = result['nb_commentaires_utilisateur']

    if nb_commentaires_utilisateur >= 3:
        flash(u'Vous avez atteint le quota maximum de 3 commentaires pour cet article !', 'danger')
        return redirect('/client/article/details?id_article=' + id_article)

    # Insertion du nouveau commentaire si quota non atteint
    tuple_insert = (commentaire, id_client, id_article)
    sql = '''
        INSERT INTO commentaires (commentaire, id_utilisateur, article_id, date_publication)
        VALUES (%s, %s, %s, NOW())
    '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    return redirect('/client/article/details?id_article=' + id_article)


#------------SUPPRIMER COMMENTAIRE -------------------------
@client_commentaire.route('/client/commentaire/delete', methods=['POST'])
def client_comment_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    date_publication = request.form.get('date_publication', None)
    sql = '''
    DELETE FROM commentaires
    WHERE id_utilisateur = %s AND article_id = %s AND date_publication = %s
    '''
    tuple_delete = (id_client, id_article, date_publication)
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    return redirect('/client/article/details?id_article=' + id_article)





#------------LES NOTES -------------------------

#------------AJOUTER NOTE -------------------------
@client_commentaire.route('/client/note/add', methods=['POST'])
def client_note_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)
    tuple_insert = (note, id_client, id_article)
    print(tuple_insert)
    sql = '''
        INSERT INTO notes (note, id_utilisateur, article_id)
        VALUES (%s, %s, %s)
    '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    return redirect('/client/article/details?id_article=' + id_article)


#------------MODIFIER NOTE -------------------------
@client_commentaire.route('/client/note/edit', methods=['POST'])
def client_note_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)
    tuple_update = (note, id_client, id_article)
    print(tuple_update)
    sql = "UPDATE notes SET note=%s WHERE id_utilisateur=%s AND article_id=%s"
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    return redirect('/client/article/details?id_article=' + id_article)


#------------SUPPRIMER NOTE -------------------------
@client_commentaire.route('/client/note/delete', methods=['POST'])
def client_note_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    tuple_delete = (id_client, id_article)
    print(tuple_delete)
    sql = '''
    DELETE FROM notes
    WHERE id_utilisateur = %s AND article_id = %s
    '''
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    return redirect('/client/article/details?id_article=' + id_article)
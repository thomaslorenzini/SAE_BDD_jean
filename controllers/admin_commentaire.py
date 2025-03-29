from flask import Blueprint, request, render_template, redirect, session
from connexion_db import get_db

admin_commentaire = Blueprint('admin_commentaire', __name__, template_folder='templates')


@admin_commentaire.route('/admin/article/commentaires', methods=['GET'])
def admin_article_details():
    mycursor = get_db().cursor()
    id_article = request.args.get('id_article', None)

    # Récupérer les commentaires d'un article avec validation
    sql = '''
        SELECT c.id, c.commentaire, c.date_publication, c.valide, u.nom AS utilisateur_nom, c.id_utilisateur
        FROM commentaires c
        JOIN utilisateur u ON c.id_utilisateur = u.id_utilisateur
        WHERE c.article_id = %s
        ORDER BY c.date_publication DESC
    '''
    mycursor.execute(sql, (id_article,))
    commentaires = mycursor.fetchall()

    # Récupérer les infos de l'article
    sql = '''
        SELECT j.nom_jean AS nom, 
               (SELECT COUNT(*) FROM commentaires WHERE article_id = j.id_jean) AS nb_commentaires_total,
               (SELECT COUNT(*) FROM commentaires WHERE article_id = j.id_jean AND valide = TRUE) AS nb_commentaires_valider
        FROM jean j WHERE j.id_jean = %s
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()

    return render_template('admin/article/show_article_commentaires.html',
                           commentaires=commentaires,
                           article=article)


@admin_commentaire.route('/admin/article/commentaires/delete', methods=['POST'])
def admin_comment_delete():
    mycursor = get_db().cursor()
    id_commentaire = request.form.get('id_commentaire')
    id_article = request.form.get('id_article')

    sql = 'DELETE FROM commentaires WHERE id = %s'
    mycursor.execute(sql, (id_commentaire,))
    get_db().commit()

    return redirect(f'/admin/article/commentaires?id_article={id_article}')


@admin_commentaire.route('/admin/article/commentaires/repondre', methods=['POST', 'GET'])
def admin_comment_add():
    if request.method == 'GET':
        id_utilisateur = request.args.get('id_utilisateur')
        id_article = request.args.get('id_article')
        return render_template('admin/article/add_commentaire.html', id_utilisateur=id_utilisateur,
                               id_article=id_article)

    mycursor = get_db().cursor()
    id_utilisateur = session['id_user']  # Admin ID
    id_article = request.form.get('id_article')
    commentaire = request.form.get('commentaire')

    sql = '''INSERT INTO commentaires (id_utilisateur, article_id, commentaire, valide) VALUES (%s, %s, %s, TRUE)'''
    mycursor.execute(sql, (id_utilisateur, id_article, commentaire))
    get_db().commit()

    return redirect(f'/admin/article/commentaires?id_article={id_article}')


@admin_commentaire.route('/admin/article/commentaires/valider', methods=['POST', 'GET'])
def admin_comment_valider():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()

    sql = 'UPDATE commentaires SET valide = TRUE WHERE article_id = %s'
    mycursor.execute(sql, (id_article,))
    get_db().commit()

    return redirect(f'/admin/article/commentaires?id_article={id_article}')

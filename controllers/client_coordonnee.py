#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

client_coordonnee = Blueprint('client_coordonnee', __name__,
                        template_folder='templates')


@client_coordonnee.route('/client/coordonnee/show')
def client_coordonnee_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    mycursor.execute("SELECT id_utilisateur, login, email, nom FROM utilisateur WHERE id_utilisateur = %s",
                     (id_client,))
    utilisateur = mycursor.fetchone()

    mycursor.execute("SELECT id_adresse, nom, rue, code_postal, ville FROM adresse WHERE id_utilisateur = %s",
                     (id_client,))
    adresses = mycursor.fetchall()
    nb_adresses = len(adresses)

    return render_template('client/coordonnee/show_coordonnee.html'
                           , utilisateur=utilisateur
                          , adresses=adresses
                          , nb_adresses=nb_adresses
                           )

@client_coordonnee.route('/client/coordonnee/edit', methods=['GET'])
def client_coordonnee_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    mycursor.execute("SELECT id_utilisateur, login, email, nom FROM utilisateur WHERE id_utilisateur = %s",
                     (id_client,))
    utilisateur = mycursor.fetchone()
    return render_template('client/coordonnee/edit_coordonnee.html'
                           ,utilisateur=utilisateur
                           )

@client_coordonnee.route('/client/coordonnee/edit', methods=['POST'])
def client_coordonnee_edit_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom=request.form.get('nom')
    login = request.form.get('login')
    email = request.form.get('email')

    utilisateur_existe = None
    mycursor.execute("SELECT id_utilisateur FROM utilisateur WHERE (email = %s OR login = %s) AND id_utilisateur != %s",
                     (email, login, id_client))
    utilisateur_existe = mycursor.fetchone()

    if utilisateur_existe:
        flash(u'votre cet Email ou ce Login existe déjà pour un autre utilisateur', 'alert-warning')
        return render_template('client/coordonnee/edit_coordonnee.html'
                               #, user=user
                               )
    mycursor.execute("UPDATE utilisateur SET nom = %s, login = %s, email = %s WHERE id_utilisateur = %s",
                     (nom, login, email, id_client))
    get_db().commit()

    get_db().commit()
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/delete_adresse',methods=['POST'])
def client_coordonnee_delete_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse= request.form.get('id_adresse')
    mycursor.execute("DELETE FROM adresse WHERE id_adresse = %s AND id_utilisateur = %s", (id_adresse, id_client))
    get_db().commit()
    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/add_adresse')
def client_coordonnee_add_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    mycursor.execute("SELECT id_utilisateur, login, email, nom FROM utilisateur WHERE id_utilisateur = %s", (id_client,))
    utilisateur = mycursor.fetchone()
    return render_template('client/coordonnee/add_adresse.html'
                           ,utilisateur=utilisateur
                           )

@client_coordonnee.route('/client/coordonnee/add_adresse',methods=['POST'])
def client_coordonnee_add_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom= request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')
    mycursor.execute("INSERT INTO adresse (id_utilisateur, nom, rue, code_postal, ville) VALUES (%s, %s, %s, %s, %s)",
                     (id_client, nom, rue, code_postal, ville))
    get_db().commit()
    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/edit_adresse')
def client_coordonnee_edit_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.args.get('id_adresse')
    mycursor.execute(
        "SELECT id_adresse, nom, rue, code_postal, ville FROM adresse WHERE id_adresse = %s AND id_utilisateur = %s",
        (id_adresse, id_client))
    adresse = mycursor.fetchone()
    mycursor.execute("SELECT id_utilisateur, login, email, nom FROM utilisateur WHERE id_utilisateur = %s",
                     (id_client,))
    utilisateur = mycursor.fetchone()
    return render_template('/client/coordonnee/edit_adresse.html'
                           ,utilisateur=utilisateur
                           ,adresse=adresse
                           )

@client_coordonnee.route('/client/coordonnee/edit_adresse',methods=['POST'])
def client_coordonnee_edit_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom= request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')
    id_adresse = request.form.get('id_adresse')
    mycursor.execute(
        "UPDATE adresse SET nom = %s, rue = %s, code_postal = %s, ville = %s WHERE id_adresse = %s AND id_utilisateur = %s",
        (nom, rue, code_postal, ville, id_adresse, id_client))
    get_db().commit()
    return redirect('/client/coordonnee/show')

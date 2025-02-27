DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS jean;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS coupe_jean;
DROP TABLE IF EXISTS taille;
DROP TABLE IF EXISTS etat;
DROP TABLE IF EXISTS adresse;
DROP TABLE IF EXISTS utilisateur;


CREATE TABLE utilisateur
(
    id_utilisateur INT PRIMARY KEY AUTO_INCREMENT,
    login VARCHAR(50),
    email VARCHAR(50),
    password VARCHAR(255),
    role VARCHAR(50),
    nom VARCHAR(50),
    est_actif BOOLEAN
);

CREATE TABLE adresse (
    id_adresse INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    nom VARCHAR(255) NOT NULL,
    rue VARCHAR(255) NOT NULL,
    code_postal VARCHAR(10) NOT NULL,
    ville VARCHAR(100) NOT NULL,
    date_utilisation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE
);



INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom,est_actif) VALUES
(1,'admin','admin@admin.fr',
    'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988',
    'ROLE_admin','admin','1'),
(2,'client','client@client.fr',
    'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349',
    'ROLE_client','client','1'),
(3,'client2','client2@client2.fr',
    'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080',
    'ROLE_client','client2','1');



CREATE TABLE etat(
   id_etat INT,
   libelle VARCHAR(50),
   PRIMARY KEY(id_etat)
);

CREATE TABLE taille(
   id_taille INT,
   nom_taille VARCHAR(50),
   PRIMARY KEY(id_taille)
);

CREATE TABLE coupe_jean(
   id_coupe_jean INT,
   nom_coupe VARCHAR(50),
   PRIMARY KEY(id_coupe_jean)
);

CREATE TABLE commande(
   id_commande INT AUTO_INCREMENT,
   date_achat DATE,
   id_etat INT NOT NULL,
   id_utilisateur INT NOT NULL,
   id_adresse_livraison INT,
   id_adresse_facturation INT,
   PRIMARY KEY(id_commande),
   FOREIGN KEY(id_etat) REFERENCES etat(id_etat),
   FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
);

CREATE TABLE jean(
   id_jean INT,
   image VARCHAR(50),
   nom_jean VARCHAR(50),
   prix_jean DECIMAL(10, 2),
   matiere VARCHAR(50),
   couleur VARCHAR(50),
   descripton VARCHAR(50),
   fournisseur VARCHAR(50),
   marque VARCHAR(50),
   id_coupe_jean INT NOT NULL,
   id_taille INT NOT NULL,
   stock INT NOT NULL ,
   PRIMARY KEY(id_jean),
   FOREIGN KEY(id_coupe_jean) REFERENCES coupe_jean(id_coupe_jean),
   FOREIGN KEY(id_taille) REFERENCES taille(id_taille)
);

CREATE TABLE ligne_commande(
   id_commande INT,
   id_jean INT,
   prix DECIMAL(10, 2),
   quantite_commande INT,
   PRIMARY KEY(id_commande, id_jean),
   FOREIGN KEY(id_commande) REFERENCES commande(id_commande),
   FOREIGN KEY(id_jean) REFERENCES jean(id_jean)
);

CREATE TABLE ligne_panier(
   id_utilisateur INT,
   id_jean INT,
   quantite_panier INT,
   date_ajout DATE,
   PRIMARY KEY(id_utilisateur, id_jean),
   FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(id_jean) REFERENCES jean(id_jean)
);

INSERT INTO etat (id_etat, libelle) VALUES
(1, 'En attente'),
(2, 'En cours'),
(3, 'Livrée'),
(4, 'Annulée');

INSERT INTO taille (id_taille, nom_taille) VALUES
(1, 'XS'),
(2, 'S'),
(3, 'M'),
(4, 'L'),
(5, 'XL');

INSERT INTO coupe_jean (id_coupe_jean, nom_coupe) VALUES
(1, 'Slim'),
(2, 'Regular'),
(3, 'Bootcut'),
(4, 'Skinny'),
(5, 'Relaxed');

INSERT INTO jean (id_jean, image, nom_jean, prix_jean, matiere, couleur, descripton, fournisseur, marque, id_coupe_jean, id_taille, stock) VALUES
(1, 'slim_bleue.png', 'Jean Slim Bleu', 49.99, 'Denim', 'Bleu', 'Jean slim en denim bleu.', 'Levis', 'Levis', 1, 2, 10),
(2, 'regular_noir.avif', 'Jean Regular Noir', 39.99, 'Coton', 'Noir', 'Jean regular noir classique.', 'Wrangler', 'Wrangler', 2, 3 , 10),
(3, 'skinny_blanc.webp', 'Jean Skinny Blanc', 59.99, 'Denim', 'Blanc', 'Jean skinny tendance.', 'Levis', 'Levis', 4, 1, 10),
(4, 'bootcut_bleue.jpg', 'Jean Bootcut Bleu', 45.99, 'Denim', 'Bleu', 'Jean bootcut confortable.', 'Wrangler', 'Wrangler', 3, 4, 10),
(5, 'relaxed_gris.jpg', 'Jean Relaxed Gris', 55.99, 'Coton', 'Gris', 'Jean relaxed pour un style décontracté.', 'Levis', 'Levis', 5, 5, 10),
(6, 'regular_beige.webp', 'Jean Regular Beige', 42.99, 'Denim', 'Beige', 'Jean regular en tissu léger.', 'Diesel', 'Diesel', 2, 2, 10),
(7, 'slim_noir.webp', 'Jean Slim Noir', 49.99, 'Denim', 'Noir', 'Jean slim en coton stretch.', 'Levis', 'Levis', 3, 3, 15),
(8, 'skinny_bleu.jpeg', 'Jean Skinny Bleu', 39.99, 'Denim', 'Bleu', 'Jean skinny avec coupe ajustée.', 'H&M', 'H&M', 5, 2, 20),
(9, 'jogger_gris.jpeg', 'Jean Jogger Gris', 45.99, 'Denim', 'Gris', 'Jean style jogger avec taille élastique.', 'Zara', 'Zara', 4, 3, 12),
(10, 'bootcut_blanc.jpeg', 'Jean Bootcut Blanc', 55.99, 'Denim', 'Blanc', 'Jean bootcut classique avec taille haute.', 'Mango', 'Mango', 5, 4, 18),
(11, 'straight_olive.jpeg', 'Jean Straight Olive', 59.99, 'Denim', 'Olive', 'Jean coupe droite avec finition raffinée.', 'Uniqlo', 'Uniqlo', 5, 5, 25),
(12, 'momfit_bleu.jpeg', 'Jean Mom Fit Bleu', 42.99, 'Denim', 'Bleu', 'Jean coupe mom avec taille haute et jambes amples.', 'Pull&Bear', 'Pull&Bear', 5, 2, 14),
(13, 'large_noir.webp', 'Jean Large Noir', 48.99, 'Denim', 'Noir', 'Jean large avec taille haute et jambes fluides.', 'Bershka', 'Bershka', 3, 4, 22),
(14, 'cargo_marron.jpeg', 'Jean Cargo Marron', 52.99, 'Denim', 'Marron', 'Jean style cargo avec poches latérales.', 'Stradivarius', 'Stradivarius', 2, 3, 30);

INSERT INTO commande (id_commande, date_achat, id_etat, id_utilisateur) VALUES
(1, '2025-01-01', 1, 1),
(2, '2025-01-15', 2, 3),
(3, '2025-01-20', 3, 1),
(4, '2025-01-22', 4, 2);

INSERT INTO ligne_commande (id_commande, id_jean, prix, quantite_commande) VALUES
(1, 1, 49.99, 2),
(1, 2, 39.99, 1),
(2, 3, 59.99, 1),
(3, 1, 49.99, 3),
(4, 4, 45.99, 2);

INSERT INTO ligne_panier (id_utilisateur, id_jean, quantite_panier, date_ajout) VALUES
(1, 2, 1, '2025-01-10'),
(3, 3, 2, '2025-01-12'),
(1, 1, 1, '2025-01-11'),
(2, 4, 1, '2025-01-14'),
(3, 6, 2, '2025-01-15');
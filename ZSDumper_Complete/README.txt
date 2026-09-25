================================================================================
                           STELLAR FXAP DUMPER V2
================================================================================

VERSION : 2.0
EDITION : Professional
TYPE    : Application Windows Standalone

================================================================================
                                INSTALLATION
================================================================================

1. Double-cliquez sur ZSDumper.exe pour lancer l'application
2. L'assistant d'installation se lancera automatiquement au premier démarrage
3. Suivez les instructions à l'écran
4. Java JRE est requis pour certaines fonctionnalités

PRÉREQUIS :
- Windows 10/11 64-bit
- Java JRE (ou OpenJDK) installé
- Aucune installation Python requise

================================================================================
                                FONCTIONNALITÉS
================================================================================

✓ Dumper : Récupération des ressources FiveM
✓ Decrypt : Décryptage des fichiers chiffrés
✓ Fixer : Réparation des fichiers corrompus
✓ Détection automatique : Récupération IP et token depuis FiveM
✓ Interface moderne : Design avec texture et cartes stylisées
✓ Cartes élégantes : Bordures vertes, avatars avec gradient
✓ Mise à jour API : Système de mise à jour automatique
✓ Installation complète : Assistant d'installation intégré
✓ Pas de CMD : Lancement en mode fenêtré sans console

================================================================================
                                DESIGN
================================================================================

INTERFACE MODERNE AVEC TEXTURE :
- Palette de couleurs gris/vert professionnelle
- Cartes avec bordures vertes (#00b894)
- Avatars avec effet gradient simulé
- Token badges avec design moderne
- Boutons avec effets de survol
- Typographie Helvetica propre
- Espacement optimal et texture visuelle

PALETTE DE COULEURS :
- Gris foncé (#1e272e) - Fond principal
- Gris moyen (#3d4852) - Cartes
- Gris clair (#4b5563) - Éléments
- Vert (#00b894) - Accents principaux
- Vert clair (#00cec9) - Survol
- Blanc (#ffffff) - Texte principal

================================================================================
                                UTILISATION
================================================================================

DUMPER :
1. Entrez le nom du serveur et l'IP / lien cfx.re
2. Cliquez sur "Ajouter" pour ajouter la cible
3. Utilisez "Détection Auto" pour récupérer depuis FiveM
4. Cliquez sur "Dump" pour lancer la récupération

DÉTECTION AUTO :
- Ouvrez FiveM et connectez-vous à un serveur
- Cliquez sur "Détection Auto" dans ZSDumper
- L'IP et le token seront récupérés automatiquement

MISE À JOUR :
- Cliquez sur le bouton "Mise à jour" dans la sidebar
- L'application vérifiera les mises à jour disponibles
- Téléchargement et installation automatique

================================================================================
                            CONFIGURATION
================================================================================

Fichiers de configuration :
- zsdumper_install.json : Installation et paramètres
- zsdumper_config.json   : Configuration utilisateur et API

Répertoires :
- Output/   : Fichiers dumpés et décryptés
- Temp/     : Fichiers temporaires (auto-nettoyage)
- Unpacked/ : Fichiers décompressés

================================================================================
                                API DE MISE À JOUR
================================================================================

L'application utilise une API pour les mises à jour automatiques :

URL par défaut : https://api-zsdump.zinz1-dev.fr

Endpoints :
- GET /version   : Récupérer la dernière version
- GET /download  : Télécharger la mise à jour
- GET /changelog : Notes de version

La configuration de l'API peut être modifiée dans zsdumper_config.json

================================================================================
                                DÉPANNAGE
================================================================================

PROBLÈME : Fenêtre CMD qui s'ouvre
SOLUTION : L'exécutable est configuré en mode sans console (console=False).
           Utilisez ZSDumper.exe directement, pas ZSDumper.bat

PROBLÈME : Token non détecté
SOLUTION : Assurez-vous que FiveM est en cours d'exécution et connecté à un
           serveur. Essayez la "Détection Auto".

PROBLÈME : Erreur lors du dump
SOLUTION : Vérifiez que l'IP du serveur est correcte et accessible.
           Assurez-vous que Java est installé.

PROBLÈME : Mise à jour échoue
SOLUTION : Vérifiez votre connexion internet. L'API doit être accessible.
           Configurez l'URL de l'API dans zsdumper_config.json si nécessaire.

================================================================================
                                TECHNIQUE
================================================================================

Empaquetage : PyInstaller avec mode fenêtré (no-console)
Dependencies : psutil, requests, pycryptodome, tkinter
Python : Non requis pour l'utilisateur (inclus dans l'exécutable)
Design : Interface moderne avec texture et cartes stylisées

================================================================================
                                SUPPORT
================================================================================

Pour le support technique ou les questions :
- Consultez la documentation en ligne
- Contactez l'équipe de développement

================================================================================
                                LICENCE
================================================================================

Stellar FXAP Dumper V2 - Professional Edition
Usage personnel et éducatif uniquement.
Respectez les conditions d'utilisation des serveurs FiveM.

================================================================================

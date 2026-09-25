================================================================================
                           ZS DUMPER
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
✓ Interface épurée : Design moderne et minimaliste
✓ Palette violet/vert : Couleurs professionnelles
✓ Mise à jour API : Système de mise à jour automatique
✓ Installation complète : Assistant d'installation intégré
✓ Pas de CMD : Lancement en mode fenêtré sans console

================================================================================
                                DESIGN
================================================================================

INTERFACE ÉPURÉE :
- Palette très sombre (#08080b) - Fond ultra noir
- Sidebar simple (#0b0b0f) avec navigation minimale
- Violet principal (#9b72ff) - Accents et branding
- Vert accent (#57e39b) - Success et highlights
- Typographie Manrope moderne
- Cartes compactes et simples
- Petits boutons élégants
- Interface clean et professionnelle

PALETTE DE COULEURS :
- Noir ultra (#08080b) - Fond principal
- Noir sidebar (#0b0b0f) - Sidebar
- Gris foncé (#101015) - Cartes
- Violet (#9b72ff) - Accents principaux
- Vert (#57e39b) - Success et highlights
- Blanc (#f5f5f7) - Texte principal

================================================================================
                                UTILISATION
================================================================================

DUMPER :
1. Cliquez sur "+" pour ajouter une nouvelle cible
2. Entrez le nom du serveur et l'IP / lien cfx.re
3. Utilisez la détection automatique pour FiveM
4. Cliquez sur "Dump" pour lancer la récupération

NAVIGATION :
- Dumper : Page principale de récupération
- Decrypt : Décryptage des fichiers
- Fixer : Réparation des fichiers

MISE À JOUR :
- Connecté à l'API locale (port 3011)
- Vérification automatique des mises à jour
- Gestion des versions via GitHub

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

API locale : http://127.0.0.1:3011

La configuration de l'API peut être modifiée dans zsdumper_config.json

================================================================================
                                DÉPANNAGE
================================================================================

PROBLÈME : Fenêtre CMD qui s'ouvre
SOLUTION : L'exécutable est configuré en mode sans console (console=False).
           Utilisez ZSDumper.exe directement.

PROBLÈME : Token non détecté
SOLUTION : Assurez-vous que FiveM est en cours d'exécution et connecté à un
           serveur. Essayez la détection automatique.

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
Design : Interface épurée avec palette violet/vert moderne

================================================================================
                                SUPPORT
================================================================================

Pour le support technique ou les questions :
- Consultez la documentation en ligne
- Contactez l'équipe de développement

================================================================================
                                LICENCE
================================================================================

ZS Dumper — Professional Edition
Usage personnel et éducatif uniquement.
Respectez les conditions d'utilisation des serveurs FiveM.

================================================================================

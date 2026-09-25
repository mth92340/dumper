# 🛠️ ZSDumper

Outil pour extraire et déchiffrer les ressources de serveurs FiveM.

## ⚠️ AVERTISSEMENT

**Risques :** Violation ToS FiveM, bannissement, risques légaux.  
**Usage légitime uniquement :** VOS serveurs, audit de sécurité, recherche éducative.  
**Vous êtes responsable de vos actions.**

---

## � Installation Rapide

```batch
1. Installez Python 3.x (cochez "Add to PATH")
   → https://www.python.org/downloads/

2. Installez Java
   → https://www.java.com/fr/download/

3. Double-cliquez sur install.bat → IMPORTANT

4. Vérifiez :
   python --version
   java -version
```

---

## 📖 Utilisation

### Méthode Simple

```batch
1. Connectez-vous au serveur FiveM
2. Double-cliquez sur ZSDumper.bat
3. Entrez le lien : cfx.re/join/abc123
4. Tapez "all" ou les numéros des ressources : 0,2,5
5. Résultats dans Output/
```

### Trouver le lien cfx.re
- F8 dans FiveM → lien affiché
- https://5metrics.dev/resources → cherchez votre serveur

---

## � Résultats

Les fichiers extraits se trouvent dans `Output/` :
- `.lua` → Scripts décompilés
- `.js/.html/.css` → Interface NUI
- `.yft/.ytd/.ydr` → Modèles 3D (stream)
- `.meta` → Configurations GTA

### Corriger les fichiers stream (optionnel)
Si les fichiers `.yft/.ytd` ne s'ouvrent pas dans OpenIV :
1. Lancez `FIXER/FivemDecryptFixer.exe`
2. Input : `Output/resource/stream`
3. Output : `Fix/`
4. Cliquez "Fix Files"

---

## 🐛 Problèmes Courants

| Erreur | Solution |
|--------|----------|
| "Python not found" | Réinstallez Python avec "Add to PATH" |
| "FiveM process not found" | Connectez-vous au serveur FiveM avant de lancer |
| "Token not found" | Lancez en Administrateur |
| "unluac failed" | Installez Java JRE |
| Fichiers .yft corrompus | Utilisez FivemDecryptFixer.exe |

---

## ⚙️ Options Avancées

**Modifier la vitesse** : Dans `auto.py` ligne 173
```python
dumper = FiveMDumper(base_url, token, max_workers=15)  # 15 = nb threads
```

**Désactiver nettoyage** : Commentez lignes 178-186 dans `auto.py`

**Extraction sans déchiffrement** : Commentez `decryptor.start()` ligne 176

---

## � Sécurité

**Bonnes pratiques :**
- Scannez les fichiers extraits avec un antivirus
- Ne redistribuez pas les ressources obtenues
- Cherchez les backdoors dans les scripts Lua/JS :
  ```lua
  load(), loadstring(), os.execute(), io.popen()  -- ❌ SUSPECT
  ```

---

## 📊 Informations Techniques

**Compatibilité :**
- Windows 10/11 (64-bit)
- Python 3.8-3.12
- FiveM b2802+
- Lua 5.4

**Comment ça marche :**
1. Scan mémoire FiveM → Extraction du token d'authentification
2. Téléchargement des ressources chiffrées
3. Déchiffrement ChaCha20 + AES-256-CBC
4. Décompilation Lua avec unluac54.jar
5. Extraction archives RPF (véhicules, maps)

---

## 📞 Support

- Ressources : https://5metrics.dev/resources

---

*Outil éducatif - Utilisez à vos risques et périls*
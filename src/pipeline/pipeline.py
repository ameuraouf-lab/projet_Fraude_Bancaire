from pathlib import Path
import pandas as pd
import numpy as np
import logging
from datetime import datetime

            # configuration du logging

# --> Déterminer le répertoire de base du projet
base_dir = Path(__file__).resolve().parents[2] 

# --> Créer (ou vérifier l'existence) du dossier "logs" dans le projet
log_dir = base_dir / "logs"
log_dir.mkdir(exist_ok = True)  # exist_ok=True évite l'erreur si le dossier existe déjà

# --> Définir le fichier dans lequel seront enregistrés les logs
log_file = log_dir / "pipeline.log"

# ⚙️ Configuration du système de logging
logging.basicConfig (filename = log_file ,    # où écrire les logs
                     level = logging.INFO ,   # niveau minimum des messages à enregistrer (INFO = inclut INFO, WARNING, ERROR, CRITICAL)
                     format="%(asctime)s — %(levelname)s — %(message)s" ,   # structure des messages enregistrés
                    )

def load_data() -> pd.DataFrame:
    """
    Charge le fichier brut depuis data/raw/creditcard.csv
    """
    base_dir = Path(__file__).resolve().parents[2]
    raw_path = base_dir / "data" / "raw" / "creditcard.csv"

    print(f"[LOAD] Lecture du fichier brut : {raw_path}")
    logging.info(f"Lecture du fichier brut : {raw_path}")

    if not raw_path.exists():
        # On lève une erreur claire si le fichier n’existe pas
        raise FileNotFoundError(f"Le fichier {raw_path} n'existe pas .")
    try :
        df =pd.read_csv(raw_path)
    except Exception as e :
        # On log l’erreur et on la relance pour qu’elle soit gérée dans main()
        logging.exception(f"Erreur lors de la lecture de {raw_path}")
        raise e
    
    print(f"[LOAD] Données chargées : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    logging.info(f"Données chargées : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et prépare les données pour l'analyse et la visualisation.
    """
    # Log de la taille initiale
    print(f"[TRANSFORM] Taille initiale : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    logging.info(f"Taille initiale des données : {df.shape[0]} lignes, {df.shape[1]} colonnes")


    # 1) Supprimer les doublons
    df = df.drop_duplicates()
    logging.info(f"Après suppression des doublons : {df.shape[0]} lignes")

    # 2) Renommer les colonnes principales
    rename_cols = {
        "Time": "time",
        "Amount": "amount",
        "Class": "is_fraud",
    }
    df = df.rename(columns=rename_cols)

    # 3) Cible propre 0/1
    df["is_fraud"] = df["is_fraud"].astype("int8")

    # 4) Nettoyage simple des montants
    df.loc[df["amount"] < 0, "amount"] = 0

    # 5) Création de "heure"
    df["heure"] = (df["time"] // 3600).astype("int16")

    # 6) Création de "jour_simule"
    df["jour_simule"] = (df["time"] // (24 * 3600)).astype("int16")

    # 7) Montant transformé
    df["amount_log1p"] = np.log1p(df["amount"])

    # 8) Réordonner les colonnes
    colonnes_debut = [
        "time",
        "heure",
        "jour_simule",
        "amount",
        "amount_log1p",
        "is_fraud",
    ]
    autres_colonnes = [c for c in df.columns if c not in colonnes_debut]
    df = df[colonnes_debut + autres_colonnes]

    #fin transformation 
    print("[TRANSFORM] Nettoyage / transformation terminé")
    print(f"[TRANSFORM] Données finales : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    
    # Logs finaux
    logging.info("Nettoyage et transformation terminés")
    logging.info(f"Données finales : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    return df


def save_data(df: pd.DataFrame) -> None:
    """
    Sauvegarde le fichier propre dans data/processed/fraude_clean.csv
    """
    base_dir = Path(__file__).resolve().parents[2]
    processed_path = base_dir / "data" / "processed" / "fraude_clean.csv"

    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False, encoding="utf-8")
    # Log de confirmation
    print(f"[SAVE] Fichier sauvegardé dans : {processed_path}")
    logging.info(f"Fichier sauvegardé dans : {processed_path}")


def main():
    print("[PIPELINE] Début du pipeline ")
    logging.info("pipeline démarré !!") # début du pipeline
    try : 
        df_raw = load_data()                # Chargement des données 
        df_clean = transform_data(df_raw)   # Transformation des données 
        save_data(df_clean)                 # Sauvegarde des données
    except FileNotFoundError as e :
        msg =f"Fichier brut introuvale : {e}"
        print("[ERREUR]",msg)
        logging.error(msg)

    except Exception as e :
        msg = f"Erreur inattendue dans le pipeline : {e}"
        print ("[erreur]",msg)
        logging.exception("Erreur inattendue dans le pipeline")
    else :
        print("[PIPELINE] Terminé ")
        logging.info("Pipeline terminé avec succès")
    finally :
        logging.info("Fin du pipeline")


if __name__ == "__main__":
    main()

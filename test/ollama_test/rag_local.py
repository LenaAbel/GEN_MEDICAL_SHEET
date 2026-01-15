# rag_local.py
import os
import sys
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader # Or UnstructuredPDFLoader
from langchain_core.documents import Document

load_dotenv() # Optional: Loads environment variables from.env file

DATA_PATH = "data/"
PDF_FILENAME = "anesthesie.pdf"
TEXT_FILENAME = "anesthesie.txt"

# Remplacer le fallback TEXT_INPUT par le texte fourni
TEXT_INPUT = """Validation  Cs                  :  Oui
alcool                          :  Non
allergies                       :  Non Connue
Score Apfel/Vpop                :  2
Appareil auditif                :  Normal
Asa                             :  3
Atcd intubation difficile       :  NE
ATCD VAM difficile              :  NE
BMI                             :  34,09
Cathter alr                     :  Non
Date intervention               :  11/12/2025
DTM                             :  Oui
Etat dentaire                   :  Risque de bris dentaire signalé/Mauvais état
état veineux D                  :  Bon
état veineux G                  :  Bon
Etat Coronographie              :  ???
Fc                              :  97
Geste opératoire                :  MIDCAB ?/Iva biss
HDLM                            :  Score calcique élevé
Informations Consentements      :  Risque Transfusion,Risque Post-op,Intubation,Risque
Anesthésie
Modalité                        :  Réglée
Intervenant                     :  Dr KAILI
Lentilles contact               :  Non
Mallampati                      :  1
Mecanisme IM                    :  ???
Médecin Sénior :                :  Dr AUDIBERT F.
Morsure lèvre supérieure        :  Oui
Coronographie                   :  Oui
ouverture de bouche             :  Oui
PA                              :  138/91
piercing                        :  Non
poids                           :  108,0
post-opératoire                 :  Unité SI
Prieur                          :  NE
Produits Anesthésiques          :  Ropi 4.75
Rachis cervical                 :  Oui
RP                              :  Normale
SaO2                            :  96
Scanner/Echo                    :  Echo
sevrage alcool                  :  Non
sevrage tabac                   :  Non
sevrage toxicomanie             :  Non
tabac                           :  Non
taille                          :  178
Transfusion                     :  Oui
Type ALR                        :  Bloc tho ant/Serratus gauhce si MIDCAB
type d'anesthésie               :  AG+ALR
type intubation                 :  IOT
VAM obésité                     :  Oui
VAM ronflement                  :  Non
VAM barbe                       :  Non
VAM édentation                  :  Oui
VAM âge>55 ans                  :  Oui
PIT                             :  73,30
PC                              :  88,2187
CSA_sevrage_vapote              :  Non
CSA_tatouage                    :  ?
CSA_sevrage_tabac               :  Non
CSA_sevrage_alcool              :  Non
score iot                       :  0
score iot NE                    :  2
score vam NE                    :  1
Commentaire_iot_vam             :  Dent tres mauvais etat
Dent 11 et 21 vont géner à l'IOT
score vam adulte                :  3
parcours ambulatoire            :  Impossible
Euroscore_pourcentage           :  0,83
Coeur : auscultation (2)        :  Normale
Coeur : signes fonctionnels (2  :  MET > 4
CRE (2)                         :  FeVG modérément altérée 56%
Aorte non dilatée 37mm
Pas de valvulopathie
E.C.G.                          :  RSR sans trble
E.F.R. (2)                      :  ???
Echo vx du cou (2)              :  Surcharge sans SS
F.E. (2)                        :  56,00
Echo cardiaque                  :  Oui
Péricarde                       :  ???
Poumon : ausculation (2)        :  Noramle
Poumon : signes fonctionnels (  :  NYHA 2
Prélevement nez                 :  ???
Rx pulmonaire (2)               :  ???
Sinus                           :  ???
test allen droit                :  ???
test allen gauche               :  ???
Texte libre chir cardiaque (2)  :  Bitronc SS IVA et BISS
CD 50%
Antibioprophylaxie              :  Zinat 1.5
Préméd J-1                      :  Trt hab
SAUF DAPAGLIFOZINE
Pas de METFORMINE le soir
Preload 400ml
Préméd J0                       :  Trt Hab
Protocole insuline
Pas de METFORMINE
Pas de DAPAGLIFOZINE
Jeun solide H-6
Jeun liquide H-2
Pas de preload
Bilan complémentaire            :  Bio pre cec à voir/Groupe RAI à voir
Commentaires Remarques          :  1) Bio à récupérer, faite par la patient mais pas recu les resultats
2) Risque bri dentaire, McGrath d'emblée
3) Protocole insuline pré op : donner ABASAGLAR + perfuser le patient VVP posée avec G10% 40ml/h
Risq_MTEV                       :  Modéré
Risq_Diff_VAM                   :  Oui
Risq_NVPO                       :  Modéré
Risq_Diff_IOT                   :  Non
Risq_Inhalation                 :  Faible
Sexe féminin                    :  Non
Non fumeur                      :  Oui
ATCD de NVPO                    :  Non
Analgésie morphinique           :  Oui
texte asa                       :  1. Patient en bonne santé.
2. Patient présentant une atteinte modérée d'une grande fonction.
3. Patient présentant une atteinte sévère d'une grande fonction
qui n'entraine pas d'incapacité.
4. Patient présentant une atteinte sévère d'une grande fonction,
invalidante, et qui met en jeu le pronostic vital.
5. Patient moribond, dont l'espérance de vie est inférieure à 24
heures, avec ou sans chirurgie.
Chirurgie à haut risque         :  ?
Cardiopathie ischémique         :  ?
ATCD insuf card congestive      :  ?
ATCD d'AVC                      :  ?
DID                             :  ?
Créatinine>20.mg/DL(152ùM)      :  ?
medoc1                          :  ABASAGLAR 24UI le matin
:  METFORMINE 1000mg
poso2                           :  1-1-1
medoc3                          :  REPAGLINIDE 2mg
poso3                           :  1-0-1
medoc4                          :  Kardégic 75mg
poso4                           :  0-1-0
medoc5                          :  Valsartan 160mg
poso5                           :  1-0-0
medoc6                          :  Dapaglifozine 10mg
poso6                           :  1-0-0
medoc7                          :  Atorvastatine 10mg
poso7                           :  0-0-1
medoc8                          :  Trulicity 3mg SC x1/sem
medoc9                          :  Tadalafil 20mg 1 à 2x/sem
medoc10                         :  Bisoce 2.5mg
poso10                          :  1-0-0
arret1                          :  Non
arret2                          :  Non
arret3                          :  Non
arret4                          :  Non
arret5                          :  Non
relaismedoc1                    :  Dapaglifozine DDP le 08/12
traitement                      :  Oui
Posoferinj1                     :  ?
Cell Saver                      :  ?
CPT                             :  inutile
GroupeRh                        :  1ère conforme- 2ème à faire
nbr CGR                         :  2
nbr plaquettes                  :  1
Pfc                             :  non
Plaquette                       :  Aucune
RAI                             :  A faire à l'entrée
seuil transfusionnel            :  ?
Sang compatibilisé car RAI +    :  Non
Anémie pré-opératoire           :  ?
PosoFerinject2                  :  ?
PosoFerinject3                  :  ?
Acide Tranex per-op             :  ?
sc11                            :  0
sc21                            :  0
sc31                            :  0
sc41                            :  0
sc51                            :  0
sc61                            :  0
sc71                            :  0
ne11                            :  0
ne21                            :  1
ne31                            :  0
ne41                            :  0
ne51                            :  0
ne61                            :  0
ne71                            :  1
sc13                            :  0
sc23                            :  1
sc33                            :  0
sc43                            :  0
sc53                            :  1
sc63                            :  1
ne13                            :  1
ne23                            :  0
ne33                            :  0
ne43                            :  0
ne53                            :  0
ne63                            :
"""

# Nouvelle introduction projet (RÉCAPITULATIF / CONTEXTE / OBJECTIFS / MÉTHODOLOGIE)
PROJECT_INTRO = """RÉCAPITULATIF
La consultation d'anesthésiste est une étape indispensable avant tout geste anesthésique. Ces consultations commencent par un interrogatoire standardisé et systématique. La synthèse de cet interrogatoire et la retranscription des données dans les logiciels métiers destinés à l'anesthésie sont des processus longs et fastidieux qui n'apportent pas de bénéfice direct aux patients pour leur prise en charge. Une retranscription automatisée et intelligente, avec tri et hiérarchisation des données, permettrait de gagner du temps de consultation afin d'optimiser et de personnaliser l'information donnée aux patients et d'améliorer leur évaluation clinique.

CONTEXTE
Une partie importante de l’information remise au patient est donnée oralement par l’anesthésiste lors de la consultation mais le temps est limité. Nous souhaitons utiliser une solution IA pour enregistrer et compiler des informations médicales du patient afin de générer automatiquement une fiche d’information personnalisée remise au patient à la fin de la consultation. Celle-ci devra contenir des informations de complications liées au patient, à son type d’anesthésie et à la chirurgie.

OBJECTIFS
Diminuer la charge de travail répétitive et sans plus-value médicale, améliorer l'information délivrée au patient et augmenter la qualité et quantité de l’information remise au patient.

MÉTHODOLOGIE
Création d'une solution informatique sécurisée permettant de générer automatiquement une fiche d'information personnalisée sans surplus de travail pour l'anesthésiste.
"""

# Nouvelle utilité : charger le texte depuis prompt.txt (root) si présent, sinon fichier data/anesthesie.txt, sinon fallback
def load_input_text():
	"""Retourne le texte à utiliser : prompt.txt (repo root) > data/anesthesie.txt > TEXT_INPUT."""
	# try repo-root prompt.txt
	root_prompt = os.path.join(os.path.dirname(__file__), "prompt.txt")
	if os.path.isfile(root_prompt):
		with open(root_prompt, "r", encoding="utf-8") as f:
			return f.read()
	# fallback to data/anesthesie.txt as before
	filepath = os.path.join(DATA_PATH, TEXT_FILENAME)
	if os.path.isfile(filepath):
		with open(filepath, "r", encoding="utf-8") as f:
			return f.read()
	return TEXT_INPUT

def get_documents():
	"""Renvoie une liste de langchain.schema.Document contenant le texte chargé."""
	text = load_input_text()
	return [Document(page_content=text, metadata={"source": "text_input"})]

def load_documents():
    """Loads documents from the specified data path."""
    pdf_path = os.path.join(DATA_PATH, PDF_FILENAME)
    loader = PyPDFLoader(pdf_path)
    # loader = UnstructuredPDFLoader(pdf_path) # Alternative
    documents = loader.load()
    print(f"Loaded {len(documents)} page(s) from {pdf_path}")
    return documents

# rag_local.py (continued)
from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents):
    """Splits documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    all_splits = text_splitter.split_documents(documents)
    print(f"Split into {len(all_splits)} chunks")
    return all_splits

from langchain_ollama import OllamaEmbeddings

def check_ollama_server():
    """Check if Ollama server is running."""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama server is running")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print("✗ ERROR: Ollama server is not running!")
    print("\nPlease start Ollama server with:")
    print("  ollama serve")
    print("\nThen ensure the embedding model is available:")
    print("  ollama pull nomic-embed-text")
    print("\nAnd the LLM model:")
    print("  ollama pull qwen3:8b")
    return False

def get_embedding_function(model_name="nomic-embed-text"):
    """Initializes the Ollama embedding function."""
    try:
        embeddings = OllamaEmbeddings(model=model_name)
        print(f"Initialized Ollama embeddings with model: {model_name}")
        return embeddings
    except Exception as e:
        print(f"✗ ERROR: Failed to initialize embeddings: {e}")
        print(f"\nMake sure the model is available:")
        print(f"  ollama pull {model_name}")
        sys.exit(1)

from langchain_community.vectorstores import Chroma

CHROMA_PATH = "chroma_db" # Directory to store ChromaDB data

def get_vector_store(embedding_function, persist_directory=CHROMA_PATH):
    """Initializes or loads the Chroma vector store."""
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_function
    )
    print(f"Vector store initialized/loaded from: {persist_directory}")
    return vectorstore

def index_documents(chunks, embedding_function, persist_directory=CHROMA_PATH):
    """Indexes document chunks into the Chroma vector store."""
    print(f"Indexing {len(chunks)} chunks...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=persist_directory
    )
    # NOTE: Chroma 0.4+ persists automatically; avoid deprecated persist()
    print(f"Indexing complete. Data saved to: {persist_directory}")
    return vectorstore


from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def create_rag_chain(vector_store, llm_model_name="qwen3:8b", context_window=8192):
    """Creates the RAG chain."""
    # Initialize the LLM
    llm = ChatOllama(
        model=llm_model_name,
        temperature=0, # Lower temperature for more factual RAG answers
        num_ctx=context_window # IMPORTANT: Set context window size
    )
    print(f"Initialized ChatOllama with model: {llm_model_name}, context window: {context_window}")

    # Create the retriever
    retriever = vector_store.as_retriever(
        search_type="similarity", # Or "mmr"
        search_kwargs={'k': 3} # Retrieve top 3 relevant chunks
    )
    print("Retriever initialized.")

    # Define the prompt template
    template = """Answer the question based ONLY on the following context:
{context}

Question: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    print("Prompt template created.")

    # Define the RAG chain using LCEL
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
| prompt
| llm
| StrOutputParser()
    )
    print("RAG chain created.")
    return rag_chain

def query_rag(chain, question, max_query_length=4000):
    """Queries the RAG chain and prints the response."""
    print("\nQuerying RAG chain...")
    
    # Truncate question if too long for embedding
    if len(question) > max_query_length:
        print(f"Warning: Question too long ({len(question)} chars), truncating to {max_query_length} chars for retrieval")
        question_truncated = question[:max_query_length] + "..."
    else:
        question_truncated = question
    
    print(f"Question length: {len(question)} chars")
    
    try:
        response = chain.invoke(question_truncated)
        print("\nResponse:")
        print(response)
        return response
    except Exception as e:
        print(f"\n✗ ERROR during query: {e}")
        print("\nTroubleshooting:")
        print("1. Check if models are properly loaded:")
        print("   ollama list")
        print("2. Try pulling models again:")
        print("   ollama pull nomic-embed-text")
        print("   ollama pull qwen3:8b")
        print("3. Restart Ollama server:")
        print("   pkill ollama && ollama serve")
        sys.exit(1)

def compose_fiche_prompt(patient_brief: str = "") -> str:
	"""(Optionnel) Prompt générique. La version réellement utilisée est construite dans query_rag_v2()."""
	return (
		"Rédige une fiche d'information d'anesthésie destinée au patient, en français simple, "
		"sans acronymes non expliqués, et en ciblant l'intervention prévue.\n\n"
		+ patient_brief
	)

def create_rag_chain_v2(vector_store, llm_model_name="qwen3:8b", context_window=4096):
    """Creates a RAG chain with manual retrieval for better control."""
    llm = ChatOllama(
        model=llm_model_name,
        temperature=0,
        num_ctx=context_window,  # Reduced from 8192 to 4096
        timeout=120  # 2 minute timeout
    )
    print(f"Initialized ChatOllama with model: {llm_model_name}, context window: {context_window}")
    
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={'k': 2}  # Reduced from 3 to 2 chunks
    )
    print("Retriever initialized.")
    
    return llm, retriever

def query_rag_v2(llm, retriever, short_query, full_prompt, patient_input_text: str, max_context_length=2000):
    """RAG: retrieval court + génération patient-friendly avec champs ciblés."""
    print("\nQuerying RAG chain...")
    print(f"Retrieval query length: {len(short_query)} chars")

    try:
        # Step 1: Retrieve relevant documents with short query
        print("Retrieving relevant documents...")
        docs = retriever.invoke(short_query)

        # Limit context length
        context_parts = []
        total_length = 0
        for doc in docs:
            if total_length + len(doc.page_content) > max_context_length:
                break
            context_parts.append(doc.page_content)
            total_length += len(doc.page_content)

        context = "\n\n".join(context_parts)
        print(f"Retrieved {len(docs)} documents, using {len(context_parts)} (total: {total_length} chars)")

        # ---- Extract structured fields from prompt.txt ----
        def _norm(s: str) -> str:
            return " ".join(s.strip().lower().split())

        def _extract_kv(raw: str) -> dict:
            out = {}
            for line in raw.splitlines():
                if ":" not in line:
                    continue
                left, right = line.split(":", 1)
                k = _norm(left)
                v = right.strip()
                if v:
                    out[k] = v
            return out

        fields = _extract_kv(patient_input_text)

        def _get(keys, default="INCONNU"):
            for k in keys:
                v = fields.get(_norm(k))
                if v:
                    return v
            return default

        geste = _get(["intervention prévue (selon dossier, si \"?\" => à confirmer)", "geste opératoire"])
        type_anesth = _get(["type d'anesthésie", "type d'anesthesie"])
        type_iot = _get(["type intubation"])
        type_alr = _get(["type alr"])
        postop = _get(["post-opératoire", "post-opératoire"])
        date_interv = _get(["date intervention"])

        asa = _get(["asa"])
        poids = _get(["poids"])
        taille = _get(["taille"])
        bmi = _get(["bmi"])
        allergies = _get(["allergies"])
        tabac = _get(["tabac", "non fumeur"])
        transfusion = _get(["transfusion"])
        risque_dents = _get(["etat dentaire", "état dentaire"])
        risque_inhalation = _get(["risq_inhalation"])
        risque_nvpo = _get(["risq_nvpo"])
        risque_mtev = _get(["risq_mtev"])
        risque_vam = _get(["risq_diff_vam"])
        commentaire_dents = _get(["commentaire_iot_vam"])

        # Human-friendly interpretations (no acronyms in output)
        def _intervention_plain(v: str) -> str:
            v_up = v.upper()
            if "MIDCAB" in v_up:
                return "Pontage coronarien mini-invasif (chirurgie du cœur), à confirmer selon le chirurgien"
            if v.strip() == "INCONNU":
                return "INCONNU"
            return f"{v} (à reformuler en mots simples; à confirmer si incertain)"

        def _anesthesie_plain(v: str) -> str:
            v_up = v.upper()
            parts = []
            if "AG" in v_up:
                parts.append("anesthésie générale (vous dormez pendant l’opération)")
            if "ALR" in v_up:
                parts.append("anesthésie locorégionale (technique pour diminuer la douleur sur une zone)")
            if not parts and v.strip() != "INCONNU":
                parts.append(v)
            return " + ".join(parts) if parts else "INCONNU"

        def _intubation_plain(v: str) -> str:
            if v.upper().strip() in ("IOT",):
                return "mise en place d’un tube dans la trachée pour vous aider à respirer pendant l’opération"
            return "INCONNU" if v == "INCONNU" else v

        # ---- Patient-facing prompt (no unexplained acronyms / no jargon) ----
        simplified_prompt = f"""Tu rédiges une fiche d'information DESTINÉE AU PATIENT (grand public).
Interdictions:
- Aucun acronyme sans explication immédiate en toutes lettres.
- Pas de jargon médical non expliqué.
- Ne pas inventer: si "?" ou "???" => écrire "à confirmer".

Contexte médical (extraits du dossier / recommandations générales):
{context[:900]}

Informations patient (issues de la consultation):
- Intervention prévue: {_intervention_plain(geste)} (date: {date_interv})
- Type d’anesthésie prévu: {_anesthesie_plain(type_anesth)}
- Gestion des voies respiratoires: {_intubation_plain(type_iot)}
- Technique anti-douleur prévue (si mentionnée): {type_alr}
- Après l’opération: {postop}
- Allergies: {allergies}
- Poids / Taille / Indice de masse corporelle: {poids} kg / {taille} cm / {bmi}
- Tabac: {tabac}
- État de santé global (classification): {asa} (à expliquer en mots simples)
- Transfusion sanguine possible: {transfusion}
- Dents: {risque_dents}. Détail: {commentaire_dents}

Risques déjà notés dans le dossier (à reformuler en langage patient):
- Risque de caillots (phlébite/embolie): {risque_mtev}
- Risque de nausées/vomissements après l’anesthésie: {risque_nvpo}
- Risque d’inhalation (passage de liquide alimentaire dans les poumons): {risque_inhalation}
- Difficulté de ventilation au masque: {risque_vam}

SORTIE DEMANDÉE (texte uniquement, structuré):
1) TITRE
2) Votre intervention (3–6 lignes, mots simples, “à confirmer” si besoin)
3) Votre anesthésie (6–10 lignes, expliquer les étapes: endormissement, respiration assistée, douleur)
4) Risques principaux personnalisés (3 à 6 puces, langage simple, adaptés: saignement/transfusion, dents, respiration, nausées, caillots…)
5) Ce que vous devez faire avant (reprendre UNIQUEMENT les consignes présentes dans le dossier: jeûne, médicaments du diabète si mentionnés; ne rien inventer)
6) Après l’intervention (douleur, surveillance, unité de soins intensifs si prévue)
7) Glossaire (petite liste: terme -> explication en une phrase)
"""

        print(f"Final prompt length: {len(simplified_prompt)} chars")
        print("Generating response (this may take a minute)...")

        response = llm.invoke(simplified_prompt)

        print("\n" + "="*80)
        print("RESPONSE:")
        print("="*80)
        response_text = response.content if hasattr(response, 'content') else str(response)
        print(response_text)
        print("="*80)
        return response

    except Exception as e:
        print(f"\n✗ ERROR during query: {e}")
        print("\nPossible issues:")
        print("1. Ollama server crashed - check: ps aux | grep ollama")
        print("2. Model not loaded - try: ollama run qwen3:8b")
        print("3. Insufficient memory - close other applications")
        print("4. Try a smaller model: ollama pull qwen2:1.5b")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# --- Main Execution ---
if __name__ == "__main__":
    # 0. Check Ollama server is running
    if not check_ollama_server():
        sys.exit(1)
    
    # 1. Load Documents
    docs = load_documents()

    # 2. Split Documents
    chunks = split_documents(docs)

    # 3. Get Embedding Function
    embedding_function = get_embedding_function()

    # 4. Index Documents
    print("Attempting to index documents...")
    vector_store = index_documents(chunks, embedding_function)

    # 5. Create RAG Chain (v2 - with reduced context window)
    llm, retriever = create_rag_chain_v2(vector_store, llm_model_name="qwen3:8b", context_window=4096)

    # 6. Générer la fiche d'anesthésie
    patient_input_text = load_input_text()
    
    # Short query for retrieval (focusing on key medical terms)
    short_query = "anesthésie chirurgie cardiaque MIDCAB risques complications ASA obésité diabète intubation VAM"
    
    # Full prompt no longer needs PROJECT_INTRO; keep generation focused on patient + retrieved context
    full_prompt = compose_fiche_prompt(patient_input_text)
    
    print("\n" + "="*80)
    print("STARTING RAG QUERY - This may take 1-2 minutes")
    print("="*80)
    
    query_rag_v2(llm, retriever, short_query, full_prompt, patient_input_text=patient_input_text, max_context_length=1500)
import streamlit as st 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from pandas.plotting import scatter_matrix

# Charger les données avec gestion d'erreur
try:
    fichier = "BeansDataSet.csv"
    col = ["Channel", "Region", "Robusta", "Arabica", "Espresso", "Lungo", "Latte", "Cappuccino"]
    
    ventes = [f'Vente_{i}' for i in range(1, 441)]
    
    data = pd.read_csv(fichier, names=col, header=0)  # header=0 pour utiliser la première ligne comme en-tête
    data.index = ventes
    
    pd.set_option('display.width', 150)
    pd.set_option('display.float_format', '{:.2f}'.format)
    
except Exception as e:
    st.error(f'Erreur de lecture du fichier : {e}')
    st.stop()

# Initialisation de l'application Streamlit
st.title("📊 Analyse des ventes de Beans & Pods")
st.write("Cette application permet d'explorer et d'analyser les ventes de Beans & Pods.")

# Sélection du type d'analyse
st.sidebar.header("Filtres d'analyse")

# Filtre "Canal"
channel_options = ["Store", "Online"]
selected_channels = st.sidebar.multiselect("Sélectionnez le canal de vente", options=channel_options, default=channel_options)

# Filtre "Région"
region_options = ["South", "North", "Central"]
selected_regions = st.sidebar.multiselect("Sélectionnez la région", options=region_options, default=region_options)

# Logique de filtrage
data_filtered = data[(data["Channel"].isin(selected_channels)) & (data["Region"].isin(selected_regions))]

# Déterminer le produit le plus vendu et la région la plus performante
if not data_filtered.empty:
    product_columns = ["Robusta", "Arabica", "Espresso", "Lungo", "Latte", "Cappuccino"]

    # Produit le plus vendu
    top_product = data_filtered[product_columns].sum().idxmax()

    # Région la plus performante
    top_region = data_filtered.groupby("Region")[product_columns].sum().sum(axis=1).idxmax()
else:
    top_product = "Aucun produit"
    top_region = "Aucune région"



# Pagination des données filtrées
if not data_filtered.empty:
    rows_per_page = 10
    num_pages = len(data_filtered) // rows_per_page + (1 if len(data_filtered) % rows_per_page > 0 else 0)
    page = st.sidebar.slider("Sélectionnez la page", 1, num_pages, 1)
    start_idx = (page - 1) * rows_per_page
    end_idx = page * rows_per_page

    st.subheader("Visualisation des ventes")
    st.write(f"Affichage des ventes de la page {page} sur {num_pages} pages.")
    st.write(data_filtered[start_idx:end_idx])
    st.write(f"Nombre total d'enregistrements : {len(data_filtered)}")
else:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")



# Option de téléchargement des données filtrées
if st.checkbox("Télécharger les données filtrées"):
    if not data_filtered.empty:
        csv = data_filtered.to_csv(index=False)
        st.download_button(label="Télécharger CSV", data=csv, file_name='ventes_filtrees.csv', mime='text/csv')

   


# Affichage des graphiques
if not data_filtered.empty:
    st.subheader("Annalyse des données")
    product_columns = ["Robusta", "Arabica", "Espresso", "Lungo", "Latte", "Cappuccino"]

 # Graphique pour les statistiques descriptives
    st.subheader("📊 Statistiques descriptives des ventes")
    stats = data_filtered[product_columns].describe()
    st.write(stats)
    fig, ax = plt.subplots(figsize=(8, 8))
    mean_values = stats.loc['mean']
    ax.pie(mean_values, labels=mean_values.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
    ax.set_title("Répartition moyenne des ventes par produit")
    st.pyplot(fig)
    
    # Histogrammes
   # st.subheader("📉 Histogramme des variables")
    #fig, ax = plt.subplots(figsize=(15, 10))
    #data_filtered[product_columns].hist(bins=15, ax=ax, layout=(3, 3))
    #st.pyplot(fig)


    # Statistiques descriptives avec un graphique à barres
    if not data_filtered.empty:
       st.subheader("📊 Répartition des ventes par produit")
       product_sales = data_filtered[product_columns].sum()
       fig, ax = plt.subplots(figsize=(8, 6))
       sns.barplot(x=product_sales.index, y=product_sales.values, palette="viridis", ax=ax)
       ax.set_ylabel("Nombre total de ventes")
       ax.set_xlabel("Produits")
       ax.set_title("Quels sont les produits les plus vendus ?")
       st.pyplot(fig)
    
       st.write("🔍 **Interprétation :** Ce graphique montre combien de ventes chaque type de café a généré. Vous pouvez voir quels produits sont les plus populaires et sur lesquels concentrer vos efforts marketing !")
    else:
       st.warning("Aucune donnée disponible pour afficher les statistiques.")


  # Visualisation interactive des tendances par canal
    st.subheader("🌍 Analyse des tendances des ventes par canal")
    sales_trend = data_filtered.groupby("Channel")[product_columns].sum().reset_index()
    fig = px.bar(sales_trend, x="Channel", y=product_columns, barmode="group", title="Comparaison des ventes en ligne et en magasin")
    st.plotly_chart(fig)

     
    # Détection des valeurs manquantes
    st.subheader("📌 Détection des valeurs manquantes")

    missing_values = data_filtered.isnull().sum()
    missing_values = missing_values[missing_values > 0]  # Filtrer uniquement les colonnes concernées

    if missing_values.empty:
        st.write("✅ Aucune valeur manquante détectée.")
    else:
      st.write("Nombre de valeurs manquantes par colonne :")
      st.table(missing_values.to_frame(name="Valeurs manquantes"))  # Affichage compact


    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(data=data_filtered.head(5).isnull(), annot=True, cmap='plasma', fmt='1f')
    st.pyplot(fig)
    st.write("Les zones en couleur indiquent les valeurs manquantes. Plus il y en a, plus nous devons être attentifs à la qualité des données.")




    # Affichage du Pairplot1 avec le hue
    st.subheader("🔎 Relations entre les produits selon les régions")
    if 'Region' in data_filtered.columns:
        st.write("""
        Ce graphique montre comment les ventes des produits (comme Robusta, Espresso, Latte, etc.) varient dans chaque région.
        Chaque couleur représente une région différente. Par exemple, vous pouvez voir que certains produits se vendent mieux dans certaines régions. 
        Cela peut vous aider à cibler vos promotions en fonction des préférences locales.
        """)
        pairplot_fig = sns.pairplot(data_filtered, hue='Region', vars=product_columns)
        st.pyplot(pairplot_fig)
    else:
        st.warning("La colonne 'Region' est manquante pour l'utilisation du hue dans le pairplot.")

    
    
    # Affichage du Pairplot2 avec explication
    st.subheader("🔎 Relations générales entre les produits")
    st.write("""
    Ce graphique montre les relations entre différents produits. Par exemple, si les ventes de Latte augmentent, est-ce que celles de Cappuccino augmentent aussi ?
    Cela peut vous donner des idées sur quels produits vendre ensemble dans des **packs promotionnels**.
    """)
    pairplot_fig = sns.pairplot(data_filtered[product_columns])
    st.pyplot(pairplot_fig)
    


    
    # Scatter Matrix
    st.subheader("Matrice de dispersion")
    fig, ax = plt.subplots(figsize=(25, 25))
    scatter_matrix(data_filtered[product_columns], figsize=(25, 25), c='g', ax=ax)
    st.pyplot(fig)


    
    # Recommandations pour la campagne marketing
    st.subheader("🚀 Recommandations pour booster les ventes")
    st.write(f"""
    **🔍 Ce que nous avons observé :**
    - 📈 Le produit le plus vendu est **{top_product}**.
    - 🌍 La région **{top_region}** est la plus dynamique.
    - 🛒 Les ventes en ligne connaissent une forte croissance.
    
    **💡 Recommandations :**
    1️⃣ **Maximiser la disponibilité du produit star** 🎯
       - Gardez toujours un stock suffisant.
       - Proposez des offres spéciales ou des réductions.
    
    2️⃣ **Renforcer la présence en ligne** 🌐
       - Améliorez l’expérience utilisateur sur votre site.
       - Offrez des promotions exclusives aux acheteurs en ligne.
    
    3️⃣ **Capitaliser sur la région la plus performante** 📍
       - Lancez des campagnes marketing locales.
       - Organisez des événements promotionnels et des dégustations.
    
    4️⃣ **Encourager la découverte de nouveaux produits** 🆕
       - Proposez des packs découverte ou des offres groupées.
       - Faites des tests de prix pour voir ce qui fonctionne le mieux.
    
    **🚀 Avec ces stratégies, Beans & Pods peut accélérer ses ventes et fidéliser ses clients !**
    """)
else:
    st.warning("⚠️ Aucune donnée disponible pour afficher des statistiques ou des graphiques.")

# Lien vers le dépôt GitHub
st.markdown("""
    ### 📂 Code source disponible sur GitHub
    Retrouvez le code de cette analyse sur notre dépôt GitHub :
    [📎 Accéder au dépôt GitHub](https://github.com/Murielle123-web/votre-depot)
""")

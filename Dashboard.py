import base64
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# KONFIGURASI HALAMAN DAN INISIALISASI STATE
st.set_page_config(
    page_title="Nowcasting PDRB",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# inisialisasi session state untuk menyimpan halaman aktif
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard' # halaman default saat pertama dibuka

try:
    page_from_url = st.query_params.get('page')
    if page_from_url:
        st.session_state.page = page_from_url
except:
    st.session_state.page = 'dashboard'

# CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');
    .block-container { 
            padding-top: 0rem !important; 
            padding-bottom: 0.5rem !important; 
            padding-left: 0.8rem !important; 
            padding-right: 0.8rem !important; 
            margin-top: 0 !important; }

    #MainMenu, header, footer {visibility: hidden;}
    .css-1lcbmhc {display: none;}
            
    .stApp { 
            background-color: #F3EFEF !important; }

    .header-navbar { 
            margin-top: 0 !important; 
            margin-bottom:0 !important; 
            background: #d9d9d9; 
            padding: 1rem 1.2rem 1rem 1.2rem; 
            border-radius: 16px; }

    .header-title { 
            font-weight: bold; 
            font-size: 1rem; 
            line-height: 1.12; 
            color: #003153; 
            letter-spacing: 0.3px; }

    .header-title i { 
            font-style: italic; }

    .header-nav { 
            display: flex; 
            align-items: 
            center; gap: 10px; }

    .nav-link { 
            color: #003153 !important; 
            text-decoration: none !important; 
            font-size: 0.7rem; 
            padding-bottom: 3px; 
            position: relative; 
            transition: color 0.2s; }

    .nav-link.dashboard { 
            margin-right: 18px; }

    .nav-link:hover::after, .nav-link.active::after { 
            content: ''; 
            display: block; 
            position: absolute; 
            left: 0; 
            right: 0; 
            bottom: 0; 
            height: 3px; 
            border-radius: 2px; 
            background: #E0A84B; }

    .color-circle { 
            display: inline-block; 
            width: 20px; 
            height: 20px; 
            border-radius: 50%; }

    .color-circle.one { 
            background: #003153; 
            margin-left: 18px; }

    .color-circle.two { 
            background: #E0A84B; }

    .color-circle.three { 
            background: #CA613A; }

    .header-title, .nav-link, .header-title i { 
            font-family: 'Montserrat', Arial, sans-serif !important; 
            letter-spacing: 0.2px; }

    .kpi-title { 
            color: #545454; 
            font-size: 0.8rem; 
            margin-bottom: -5px; 
            margin-top: 10px; 
            padding-left: 13px; }

    .shap-title { 
            color: #545454; 
            font-size: 0.8rem; 
            margin:-5px 0 5px 0; 
            padding-left: 17px; 
            display: flex; 
            align-items: center; 
            gap: 8px; }

    .download-btn button { 
            font-size: 0.7rem; 
            padding: 0.13rem 0.8rem; 
            margin:0 0 8px 0; 
            border-radius: 10px; 
            color: #545454; 
            background: #FFFFFF; 
            border: 0px; 
            box-shadow: 0 2px 10px #00000008; 
            cursor: pointer; 
            transition: 0.2s all; }

    .download-btn button:hover { 
            background: #CA613A; 
            color: #FFFFFF; 
            border-color: #CA613A; 
            box-shadow: 0 4px 18px #00336622; }

    .about-subheader {
            color: #003153 !important; 
            font-weight: semi-bold !important;
            font-size: 1rem !important; 
            padding-top: 0 !important; 
            padding-bottom: 0 !important; 
            margin-top: 0 !important; 
            margin-bottom: 5px !important;
    }

    /* biar sub-judul pertama tidak terlalu jauh jaraknya */
    .about-subheader:first-of-type {
            margin-top: 0rem;
    }
            
    .about-page-text {
            color: #545454 !important; 
            font-size: 0.9rem !important; 
            line-height: 1.2 !important; /* jarak antar baris */
    }

    /* atur jarak di dalam expander */
    .expander-list ul > li {
        margin-top: 0.7rem; /* Menambahkan jarak di atas setiap poin utama */
    }

    /* menghilangkan jarak atas untuk poin pertama agar tidak terlalu jauh dari judul expander */
    .expander-list ul > li:first-child {
        margin-top: 0;
    }

    div[data-testid="stVerticalBlock"] div[data-testid="stStyledFullScreenFrame"] { 
            margin-top: -65px !important; }

    .stMarkdown { 
            margin-bottom: -15px !important; }

            
    /* === STYLING UNTUK KARTU KPI (st.metric) === */

    /* mengatur wadah/kartu st.metric */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-bottom: 5px solid #E0A84B;
        border-radius: 10px;
        padding: 10px;
        padding-left: 13px;
        text-align: left;
    }

    /* mengatur tulisan label (Contoh: "Q1 2025") */
    div[data-testid="stMetricLabel"] {
        font-size: 0.7rem;
        font-weight: 300;
        color: #545454;
    }

    /* mengatur angka utama (Contoh: "Rp91.230 miliar") */
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
        font-weight: bold;
        color: #545454;
    }

    /* mengatur teks perbandingan (Contoh: "+2.1% dari...") */
    div[data-testid="stMetricDelta"] {
        font-size: 0.8rem;
        font-weight: 500;
    }

</style>
""", unsafe_allow_html=True)


# HEADER
active_page = st.session_state.page
st.markdown(f"""
<div class="header-navbar" style="display: flex; justify-content: space-between; align-items: center;">
    <div class="header-title">
        <i>NOWCASTING</i> PDRB INDUSTRI PENGOLAHAN<br>PROVINSI JAWA TIMUR
    </div>
    <div class="header-nav">
        <a href="/?page=dashboard" target="_self" class="nav-link dashboard{' active' if active_page == 'dashboard' else ''}">DASHBOARD</a>
        <a href="/?page=about" target="_self" class="nav-link{' active' if active_page == 'about' else ''}">ABOUT</a>
        <span class="color-circle one"></span>
        <span class="color-circle two"></span>
        <span class="color-circle three"></span>
    </div>
</div>
""", unsafe_allow_html=True)

# UNTUK MEMBACA URL DAN MENGUPDATE STATE 
try:
    page_from_url = st.query_params.get('page')
    if page_from_url:
        st.session_state.page = page_from_url
except:
    st.session_state.page = 'dashboard'


# ==== HALAMAN DASHBOARD ====
if st.session_state.page == 'dashboard':   
    @st.cache_data
    def load_data():
        # membaca data aktual dan hasil prediksi dari file CSV
        pdrb_data = pd.read_csv("prediksi_aktual.csv")
        # mengubah nama kolom agar sesuai dengan kode grafik yang sudah ada
        pdrb_data = pdrb_data.rename(columns={
            'Unnamed: 0': 'Periode',  # mengubah nama kolom pertama yang kosong
            'Predict': 'Prediksi',   # mengubah 'Predict' menjadi 'Prediksi'
            'gdp': 'Aktual'          # mengubah 'gdp' menjadi 'Aktual'
        })

        # membaca data SHAP dari file CSV
        shap_data = pd.read_csv("shap_values.csv")

        # membaca data fitur dari file CSV
        fitur_data = pd.read_csv("fitur.csv")
        fitur_data = fitur_data.rename(columns={'triwulan': 'Periode'})

        return pdrb_data, shap_data, fitur_data

    pdrb_df, shap_df, fitur_df = load_data()


    row1_col1, row1_col2 = st.columns([0.35, 0.65], gap='small')

    # KPI Card
    def create_kpi_data(df):
        df = df.sort_values('Periode').reset_index(drop=True)
        # jika ada nilai kosong di 'Aktual', isi dengan data dari 'Prediksi'.
        df['Nilai_Tampil'] = df['Aktual'].fillna(df['Prediksi'])
        # perhitungan persentase
        df['pct_change'] = df['Nilai_Tampil'].pct_change()
        # ambil 4 triwulan terakhir untuk ditampilkan
        kpi_df = df.tail(4).copy()
        # bikin label untuk periode pembanding dgn triwulan sebelumnya
        kpi_df['periode_pembanding'] = df['Periode'].shift(1).tail(4)

        # format penulisan
        kpi_df['Nilai'] = kpi_df['Nilai_Tampil'].apply(lambda x: f"Rp{x:,.0f} miliar".replace(',', '.'))

        kpi_df['Perbandingan'] = kpi_df.apply(
            lambda row: f"{row['pct_change']:+.2%} dari {row['periode_pembanding']}", axis=1 # format sebagai persentase
        )

        # st.metric akan mencari paramater bernama label, agar mudah ganti kolom Periode jadi Label
        kpi_df = kpi_df.rename(columns={'Periode': 'Label'})
        kpi_df = kpi_df.iloc[::-1] # balik urutann agar triwulan terbaru di atas
        return kpi_df

    with row1_col1:
        # VISUALISASI KPI 
        st.markdown('<div class="kpi-title">Hasil Prediksi Terkini</div>', unsafe_allow_html=True)

        kpi_df = create_kpi_data(pdrb_df)

        kpi_1 = kpi_df.iloc[0]
        kpi_2 = kpi_df.iloc[1]
        kpi_3 = kpi_df.iloc[2]
        kpi_4 = kpi_df.iloc[3]

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label=kpi_1['Label'], value=kpi_1['Nilai'], delta=kpi_1['Perbandingan'])
        with col2:
            st.metric(label=kpi_2['Label'], value=kpi_2['Nilai'], delta=kpi_2['Perbandingan'])

        col3, col4 = st.columns(2)
        with col3:
            st.metric(label=kpi_3['Label'], value=kpi_3['Nilai'], delta=kpi_3['Perbandingan'])
        with col4:
            st.metric(label=kpi_4['Label'], value=kpi_4['Nilai'], delta=kpi_4['Perbandingan'])


        # VISUALISASI SHAP VALUE TIAP FITUR
        with st.container():
            st.markdown(
                '<div class="shap-title";>Kepentingan Fitur Pembangun Prediksi'
                    '<span title="Model prediksi ini dibangun dengan variabel nighttime lights, kurs USD periode sebelumnya, dan nilai PDRB periode sebelumnya. Variabel-variabel ini dipilih berdasarkan tingkat kontribusi pada pemodelan yang diukur dengan SHAP values. Semakin besar mean |SHAP value| maka semakin berkontribusi terhadap hasil prediksi." '
                    'style="cursor:pointer; color:#545454; font-weight:600; margin-left:4px;">&#9432;</span>'
                '</div>',
                unsafe_allow_html=True
            )
            with st.container(border=True):
                fig_shap = go.Figure(go.Bar(
                    y=shap_df['fitur'], # ambil kolom fitur             
                    x=shap_df['mean_shap_value'],  # ambil kolom mean_shap_value
                    orientation='h',
                    marker_color='#E0A84B',
                    text=shap_df['mean_shap_value'].round(3),
                    textposition='outside',
                    insidetextanchor='start'
                ))
                
                fig_shap.update_layout(
                    xaxis_title="Mean |SHAP Value|",
                    yaxis={'categoryorder':'total ascending'},
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b=0),
                    plot_bgcolor='#F3EFEF', paper_bgcolor='#F3EFEF',
                    height=130,
                    width=100,
                )
                st.plotly_chart(fig_shap, use_container_width=True)

    # VISUALISASI PREDIKSI VS AKTUAL
    with row1_col2:
        with st.container():
            st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
            sub_col1, sub_col2 = st.columns([0.7, 0.3])
            with sub_col1:
                st.markdown('<span style="font-size:1rem; color:#003153; font-weight:600; padding: 0; margin:0;">Hasil Prediksi dan Data Aktual</span>', unsafe_allow_html=True)
            with sub_col2:
                csv = pdrb_df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                download_button_html = f"""<div style='display: flex; justify-content: flex-end; align-items: center; height: 100%;'><a class="download-btn" href="data:file/csv;base64,{b64}" download="prediksi_pdrb.csv" style="text-decoration: none;"><button>Download CSV</button></a></div>"""
                st.markdown(download_button_html, unsafe_allow_html=True)
            with st.container(border=True):
                fig_pred = go.Figure()
                fig_pred.add_trace(go.Scatter(x=pdrb_df['Periode'], y=pdrb_df['Prediksi'], name='Prediksi', line=dict(color='#003153', width=3)))
                fig_pred.add_trace(go.Scatter(x=pdrb_df['Periode'], y=pdrb_df['Aktual'], name='Aktual', line=dict(color='#E0A84B', width=3)))
                fig_pred.update_layout( 
                    yaxis_title="Miliar Rupiah", 
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), 
                    margin=dict(l=0, r=20, t=0, b=40), 
                    plot_bgcolor='#F3EFEF', 
                    paper_bgcolor='#F3EFEF', 
                    height=353,
                    xaxis=dict(tickangle=-45),
                     )
                st.plotly_chart(fig_pred, use_container_width=True)

    # VISUALISASI FITUR
    row2_col1, row2_col2 = st.columns(2, gap="small")

    def create_feature_chart(data, feature_column):
        fig = go.Figure(go.Scatter(x=data['Periode'], y=data[feature_column], line=dict(color='#003153', width=2)))

        fig.update_layout(
            xaxis=dict(tickfont=dict(size=11),
                       tickangle=-45),
            yaxis=dict(
                # title=dict(text="Satuan Fitur", font=dict(size=11)),
                tickfont=dict(size=11)
            ),
            showlegend=False, 
            height=200, 
            margin=dict(l=5, r=5, t=5, b=5), 
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    with row2_col1:
        with st.container(border=True):
            st.markdown('<b style="color: #003153; font-size: 0.8rem; padding: 0; margin: 0;">Nighttime Lights (NTL)</b>', unsafe_allow_html=True)
            st.plotly_chart(create_feature_chart(fitur_df, 'ntl'), use_container_width=True)

    with row2_col2:
        with st.container(border=True):
            st.markdown('<b style="color: #003153; font-size: 0.8rem; padding: 0; margin: 0;">Kurs USD</b>', unsafe_allow_html=True)
            st.plotly_chart(create_feature_chart(fitur_df, 'kurs'), use_container_width=True)

    # FOOTER untuk halaman Dashboard
    st.markdown("""
        <hr style="margin-top:2rem; margin-bottom:0.5rem; border: 1px solid #e0e0e0;" />
        <div style="text-align:center; font-size:0.85rem; color:#545454;">
            Developed by <b>Khuzaimah Putri</b> (<a href="mailto:222112137@stis.ac.id" style="color:#CA613A; text-decoration:none;">222112137@stis.ac.id</a>)<br>
            Supervised by Prof. Setia Pramana, S.Si, M.Sc, Ph.D<br>
            <span style="font-size:0.7rem; color:#CA613A; padding-bottom: 8px;">v1.0 — Juni 2025</span>
        </div>
    """, unsafe_allow_html=True)




# ==== HALAMAN ABOUT ====
elif st.session_state.page == 'about':
    # menambahkan sedikit padding dengan markdown baru atas agar tidak terlalu mepet header
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)


    # BAGIAN PERTAMA (TENTANG PROYEK)
    st.markdown('<h2 class="about-subheader">Tentang Proyek Ini</h2>', unsafe_allow_html=True)
    st.markdown("""
    <p class="about-page-text">
        <i>Dashboard</i> ini memvisualisasikan hasil prediksi PDRB Sektor Industri Pengolahan Provinsi Jawa Timur yang membantu pemantauan perkembangan ekonomi 
        secara lebih cepat untuk mengatasi masalah keterlambatan rilis data resmi. <i>Dashboard</i> ini dibangun sebagai artefak skripsi mahasiswa 
        Politeknik Statistika STIS program studi D-IV Komputasi Statistik.
    </p>
    """, unsafe_allow_html=True)


    # BAGIAN KEDUA (DATA DAN METODOLOGI)
    st.markdown('<h2 class="about-subheader">Data dan Metodologi</h2>', unsafe_allow_html=True)
    st.markdown("""
    <p class="about-page-text">
        Data yang digunakan merupakan gabungan dari beberapa sumber 
        dengan beberapa kandidat model <i>machine learning</i>.
    </p>
    """, unsafe_allow_html=True)

    # expander
    with st.expander("Lihat Detail Sumber Data dan Model"):
        st.markdown("""
        <div class="expander-list">

        * Sumber Data:
            * *Official Statistics* yang diperoleh dari Badan Pusat Statistik (BPS) dan Bank Indonesia (BI)
            * Citra Satelit yang diperoleh dari SNPP-VIIRS, Aura/OMI, dan Terra/MODIS
            * Google Trends Index yang diakses dari *trends.google.com*
        
        * Pendekatan Pemodelan:
            * *Machine Learning* dengan beberapa kandidat model, yaitu:
                * Ridge
                * Lasso
                * ElasticNet
                * Random Forest
                * Gradient Boosting
                * XGBoost
            * Model *machine learning* juga dibandingkan dengan pendekatan ARIMA/ARIMAX
            * *Feature Selection* yang digunakan merupakan perbandingan dari korelasi Pearson dan SHAP-Select

        </div>
        """, unsafe_allow_html=True)

    # highlight model
    st.info("""
    Model terbaik yang diperoleh adalah Ridge Regression
            dengan fitur akhir ***Nighttime Lights***, **Kurs USD periode sebelumnya**, dan **nilai PDRB periode sebelumnya**.
    """, icon="💡")

    with st.expander("Lihat Detail Cakupan Wilayah Nighttime Lights"):
        st.markdown("""
        <div class="expander-list">

        * *Nighttime Lights* difokuskan pada wilayah industri teratas di Jawa Timur dan mempertimbangkan ketersediaan kawasan industri besar. Berikut wilayah-wilayah tersebut:
            * Kota Surabaya
            * Sidoarjo
            * Kota Kediri
            * Pasuruan
            * Gresik
            * Mojokerto
            * Tuban
        </div>
        """, unsafe_allow_html=True)


    # BAGIAN KETIGA (PENGEMBANG DAN PEMBIMBING)
    st.markdown('<h2 class="about-subheader">Pengembang dan Pembimbing</h2>', unsafe_allow_html=True)
    
    # kolom pemisah text dan profil linkedin
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        st.markdown("""
        <p class="about-page-text">
        Proyek ini disusun dan dikembangkan oleh <b>Khuzaimah Putri</b>. 
        Seluruh proses penelitian dan pengembangan <i>dashboard</i> berada di bawah bimbingan <b>Prof. Setia Pramana, S.Si, M.Sc, Ph.D.</b>
        </p><br>
        """, unsafe_allow_html=True)
        
    with col2:
        # tombol link ke profil LinkedIn
        st.link_button("🔗 Profil LinkedIn Developer", "https://linkedin.com/in/khuzaimahputri/", use_container_width=True)


    # FOOTER untuk halaman About agar konsisten
    st.markdown("""
        <hr style="margin-top:2rem; margin-bottom:0.5rem; border: 1px solid #e0e0e0;" />
        <div style="text-align:center; font-size:0.85rem; color:#545454;">
            Developed by <b>Khuzaimah Putri</b> (<a href="mailto:222112137@stis.ac.id" style="color:#CA613A; text-decoration:none;">222112137@stis.ac.id</a>)<br>
            Supervised by Prof. Setia Pramana, S.Si, M.Sc, Ph.D<br>
            <span style="font-size:0.7rem; color:#CA613A; padding-bottom: 8px;">v1.0 — Juni 2025</span>
        </div>
    """, unsafe_allow_html=True)

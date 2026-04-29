import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style='dark')

# menyiapkan dan membaca data
day_df = pd.read_csv('dashboard/day.csv')
hour_df = pd.read_csv('dashboard/hour.csv')

# membersihkan data dan modifikasi persis di notebook
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
day_df['season'] = day_df['season'].map(season_mapping)

weather_mapping = {1: 'Clear', 2: 'Misty', 3:'Light Rain', 4: 'Heavy Rain'}
day_df['weathersit'] = day_df['weathersit'].map(weather_mapping)

label_hari = {0: 'Libur/Akhir Pekan', 1: 'Hari Kerja'}
hour_df['keterangan_hari'] = hour_df['workingday'].map(label_hari)

def categorize_time(hour):
    if 5 <= hour <= 11:
        return 'Pagi (05-11)'
    elif 12 <= hour <= 16:
        return 'Siang (12-16)'
    elif 17 <= hour <= 20:
        return 'Sore (17-20)'
    else:
        return 'Malam (21-04)'
    
hour_df['time_cluster'] = hour_df['hr'].apply(categorize_time)

#fitur batasan tanggal
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

# membuat dashboard streamlit
## judul utama
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
st.header('Bike Sharing Dashboard')

## sidebar
with st.sidebar:
    st.image('https://cdn-icons-png.flaticon.com/512/2972/2972185.png', width = 110)
    st.title('Fatimah Azzahra - CDCC794D6X0379')
    st.write('Proyek Analisis Data - CodingCamp')
    st.markdown('---')

    st.subheader('Filter Data')


    if "date_filter" not in st.session_state:
        st.session_state.date_filter = (min_date, max_date)

    # tombol reset
    if st.button('Reset Filter'):
        st.session_state.date_filter = (min_date, max_date)

    # filter rentang waktu
    date_range = st.date_input(
        label = 'Rentang Waktu',
        min_value = min_date,
        max_value = max_date,
        value = st.session_state.date_filter,
        key = 'date_filter'
    )

    
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = date_range[0], date_range[0]

main_df = day_df[(day_df["dteday"] >= str(start_date)) & (day_df["dteday"] <= str(end_date))]

## membuat metrik ringkasan
st.subheader('Daily Data Overview')
col1, col2, col3 = st.columns(3)

with col1:
    st.metric('Total Rides', value = f"{main_df['cnt'].sum():,}")
with col2:
    st.metric('Registered Users', value = f"{main_df['cnt'].sum():,}")
with col3:
    st.metric('Casual Users', value = f"{main_df['cnt'].sum():,}")

st.markdown('---')

## grafik 1 : cuaca
st.subheader('1. Bagaimana Pengaruh Cuaca Terhadap Penyewaan?')
fig1, ax1 = plt.subplots(figsize = (10, 6))

weather_rentals = main_df.groupby('weathersit')['cnt'].mean().reset_index().sort_values(by = 'cnt', ascending = False)

sns.barplot(
    x = 'weathersit', 
    y = 'cnt',
    data = weather_rentals,
    palette = 'viridis',
    ax = ax1 )

ax1.set_xlabel('Kondisi Cuaca')
ax1.set_ylabel('Rata-rata Penyewaan Harian')
st.pyplot(fig1)

st.markdown('---')

## grafik 2 : jam sibuk
st.subheader("2. Kapan Jam Puncak Penyewaan Sepeda?")
fig2, ax2 = plt.subplots(nrows=2, ncols=1, figsize=(10, 12))

hourly_rentals = hour_df.groupby(['keterangan_hari', 'hr'])['cnt'].mean().reset_index()
cluster_rentals = hour_df.groupby(['keterangan_hari', 'time_cluster'])['cnt'].mean().reset_index()

sns.lineplot(
    x = 'hr',
    y = 'cnt',
    hue = 'keterangan_hari',
    data = hourly_rentals,
    marker = 'o',
    palette = 'Set1',
    ax = ax2[0])

ax2[0].set_title('Pola Penyewaan per Jam', fontsize=14)

sns.barplot(
    x = 'time_cluster',
    y = 'cnt',
    hue = 'keterangan_hari',
    data = cluster_rentals,
    palette = 'Set2',
    ax = ax2[1])

ax2[1].set_title('Pola Penyewaan per Cluster Waktu', fontsize=14)
plt.tight_layout()
st.pyplot(fig2)

st.markdown('---')

## grafik 3 : perilaku pengguna
st.subheader("3. Perbandingan Pengguna Casual vs Registered Berdasarkan Musim")
season_users = main_df.groupby('season')[['casual', 'registered']].sum().reset_index()
season_users_melted = pd.melt(season_users, id_vars=['season'], value_vars=['casual', 'registered'], var_name='user_type', value_name='total_rentals')

fig3, ax3 = plt.subplots(figsize=(10, 6))

sns.barplot(
    x = 'season',
    y = 'total_rentals',
    hue = 'user_type',
    data = season_users_melted,
    palette = 'muted',
    ax = ax3)

ax3.set_xlabel("Musim")
ax3.set_ylabel("Total Penyewaan")
st.pyplot(fig3)

## penutup
st.caption("Copyright (c) Fatimah Azzahra 2026")
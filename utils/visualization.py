# Fungsi-fungsi untuk visualisasi data
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_visualization(df, column_names=None):
    """Membuat visualisasi data dari DataFrame"""
    try:
        if column_names is None or len(column_names) == 0:
            # Pilih kolom numerik secara otomatis
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower()]
        else:
            numeric_cols = column_names
            date_cols = []
        
        if not numeric_cols:
            st.warning("Tidak ada kolom numerik untuk divisualisasikan.")
            return
        
        # Buat tab untuk berbagai visualisasi
        viz_tabs = st.tabs(["📊 Statistik", "📈 Line Chart", "📊 Bar Chart", "🔄 Scatter Plot", "🥧 Pie Chart"])
        
        # Tab Statistik
        with viz_tabs[0]:
            st.subheader("Statistik Dasar")
            st.dataframe(df.describe())
            
            # Korelasi
            if len(numeric_cols) > 1:
                st.subheader("Matriks Korelasi")
                corr = df[numeric_cols].corr()
                fig = px.imshow(corr, 
                                text_auto=True, 
                                color_continuous_scale='RdBu_r',
                                title="Korelasi antar Variabel Numerik")
                st.plotly_chart(fig, use_container_width=True)
        
        # Tab Line Chart
        with viz_tabs[1]:
            st.subheader("Line Chart")
            
            # Deteksi kolom waktu untuk x-axis
            if date_cols:
                x_axis = st.selectbox("Pilih kolom untuk sumbu X (waktu):", date_cols)
                y_axis = st.multiselect("Pilih kolom untuk sumbu Y:", numeric_cols, default=[numeric_cols[0]] if numeric_cols else [])
                
                if y_axis:
                    fig = px.line(df, x=x_axis, y=y_axis, title=f"Tren berdasarkan {x_axis}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Tidak terdeteksi kolom tanggal. Menggunakan index sebagai sumbu X.")
                y_axis = st.multiselect("Pilih kolom untuk sumbu Y:", numeric_cols, default=[numeric_cols[0]] if numeric_cols else [])
                
                if y_axis:
                    fig = px.line(df, y=y_axis, title="Tren Data")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Tab Bar Chart
        with viz_tabs[2]:
            st.subheader("Bar Chart")
            
            # Pilih kolom kategori dan nilai
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            if categorical_cols:
                x_axis = st.selectbox("Pilih kolom kategori untuk sumbu X:", categorical_cols)
                y_axis = st.selectbox("Pilih kolom nilai untuk sumbu Y:", numeric_cols, index=0 if numeric_cols else None)
                
                if y_axis:
                    # Hitung agregasi
                    agg_func = st.selectbox("Fungsi agregasi:", ["sum", "mean", "count", "min", "max"])
                    df_agg = df.groupby(x_axis)[y_axis].agg(agg_func).reset_index()
                    
                    fig = px.bar(df_agg, x=x_axis, y=y_axis, title=f"{agg_func.capitalize()} dari {y_axis} berdasarkan {x_axis}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Tidak ada kolom kategori yang tersedia untuk Bar Chart.")
        
        # Tab Scatter Plot
        with viz_tabs[3]:
            st.subheader("Scatter Plot")
            
            if len(numeric_cols) >= 2:
                x_axis = st.selectbox("Pilih kolom untuk sumbu X:", numeric_cols, index=0)
                y_axis = st.selectbox("Pilih kolom untuk sumbu Y:", numeric_cols, index=min(1, len(numeric_cols)-1))
                
                color_col = None
                if categorical_cols:
                    use_color = st.checkbox("Tambahkan warna berdasarkan kategori?")
                    if use_color:
                        color_col = st.selectbox("Pilih kolom untuk warna:", categorical_cols)
                
                fig = px.scatter(df, x=x_axis, y=y_axis, color=color_col,
                                 title=f"Scatter Plot {y_axis} vs {x_axis}")
                
                # Tambahkan garis tren
                add_trendline = st.checkbox("Tambahkan garis tren?")
                if add_trendline:
                    fig.update_layout(showlegend=True)
                    fig.add_trace(go.Scatter(
                        x=df[x_axis],
                        y=df[y_axis].values,
                        mode='markers',
                        showlegend=False,
                        opacity=0
                    ))
                    fig = px.scatter(df, x=x_axis, y=y_axis, color=color_col,
                                     trendline="ols", title=f"Scatter Plot {y_axis} vs {x_axis}")
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Diperlukan minimal 2 kolom numerik untuk Scatter Plot.")
        
        # Tab Pie Chart
        with viz_tabs[4]:
            st.subheader("Pie Chart")
            
            if categorical_cols:
                category_col = st.selectbox("Pilih kolom kategori:", categorical_cols)
                value_col = st.selectbox("Pilih kolom nilai (opsional):", [None] + numeric_cols)
                
                if value_col:
                    # Agregasi data
                    pie_data = df.groupby(category_col)[value_col].sum().reset_index()
                    fig = px.pie(pie_data, names=category_col, values=value_col, 
                                title=f"Distribusi {value_col} berdasarkan {category_col}")
                else:
                    # Hitung frekuensi
                    pie_data = df[category_col].value_counts().reset_index()
                    fig = px.pie(pie_data, names="index", values=category_col, 
                                title=f"Distribusi {category_col}")
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Tidak ada kolom kategori untuk Pie Chart.")
        
    except Exception as e:
        st.error(f"Error membuat visualisasi: {str(e)}")

def visualize_financial_data(df):
    """Visualisasi khusus untuk data keuangan"""
    # Deteksi kolom keuangan
    financial_cols = [col for col in df.columns if any(term in col.lower() 
                     for term in ['revenue', 'profit', 'sales', 'cost', 'expense', 
                                 'pendapatan', 'biaya', 'penjualan', 'laba', 'rugi'])]
    
    date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower() or 'tanggal' in col.lower()]
    
    if not financial_cols:
        st.warning("Tidak dapat mendeteksi kolom keuangan dalam data.")
        return
    
    st.subheader("📊 Analisis Keuangan")
    
    # Grafik tren keuangan
    if date_cols:
        date_col = st.selectbox("Pilih kolom tanggal:", date_cols)
        metrics = st.multiselect("Pilih metrik keuangan:", financial_cols, 
                               default=[financial_cols[0]] if financial_cols else [])
        
        if metrics:
            # Urutkan data berdasarkan tanggal
            df_sorted = df.sort_values(by=date_col)
            
            # Plot tren
            fig = px.line(df_sorted, x=date_col, y=metrics, 
                        title="Tren Keuangan", markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # Persentase perubahan
            st.subheader("Persentase Perubahan")
            
            pct_changes = {}
            for metric in metrics:
                df_sorted[f"{metric}_pct_change"] = df_sorted[metric].pct_change() * 100
                pct_changes[metric] = df_sorted[f"{metric}_pct_change"].mean()
            
            # Tampilkan perubahan rata-rata
            cols = st.columns(len(pct_changes))
            for i, (metric, pct) in enumerate(pct_changes.items()):
                delta_color = "normal" if abs(pct) < 1 else "inverse" if pct < 0 else "normal"
                cols[i].metric(f"Rata-rata Δ {metric}", f"{pct:.2f}%", delta=f"{pct:.2f}%", delta_color=delta_color)
    else:
        st.info("Tidak terdeteksi kolom tanggal untuk analisis tren.")
        
    # Visualisasi proporsi
    st.subheader("Proporsi Komponen Keuangan")
    
    # Pilih metrik pendapatan dan biaya
    revenue_cols = [col for col in financial_cols if any(term in col.lower() 
                   for term in ['revenue', 'sales', 'pendapatan', 'penjualan'])]
    
    expense_cols = [col for col in financial_cols if any(term in col.lower() 
                   for term in ['cost', 'expense', 'biaya'])]
    
    if revenue_cols and expense_cols:
        # Grafik waterfall
        try:
            import plotly.graph_objects as go
            
            # Ambil total pendapatan dan biaya terbaru
            latest_data = df.iloc[-1]
            
            rev_col = st.selectbox("Pilih kolom pendapatan:", revenue_cols)
            exp_cols = st.multiselect("Pilih kolom biaya:", expense_cols)
            
            if exp_cols:
                # Buat data untuk waterfall chart
                measure = ["relative"] * len(exp_cols) + ["total"]
                x = exp_cols + ["Profit"]
                
                y = [latest_data[col] * -1 for col in exp_cols]  # Biaya sebagai nilai negatif
                y.append(latest_data[rev_col] + sum(y))  # Profit = Revenue - Total Expense
                
                # Buat waterfall chart
                fig = go.Figure(go.Waterfall(
                    name="Finansial", 
                    orientation="v",
                    measure=measure,
                    x=x,
                    textposition="outside",
                    y=y,
                    connector={"line": {"color": "rgb(63, 63, 63)"}},
                ))
                
                # Tambahkan Revenue di awal
                fig.add_trace(go.Waterfall(
                    name="Revenue",
                    orientation="v",
                    measure=["absolute"],
                    x=[rev_col],
                    textposition="outside",
                    y=[latest_data[rev_col]],
                    connector={"line": {"color": "rgb(63, 63, 63)"}},
                ))
                
                fig.update_layout(
                    title="Revenue to Profit Waterfall",
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Gagal membuat waterfall chart: {str(e)}")

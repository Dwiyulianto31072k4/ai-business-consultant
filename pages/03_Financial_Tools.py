import streamlit as st
import pandas as pd
import numpy as np
import logging
import plotly.express as px
import plotly.graph_objects as go

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Business Consultant - Financial Tools",
    page_icon="💰",
    layout="wide"
)

# Header
st.title("💰 Financial Tools")
st.markdown("""
Alat keuangan untuk membantu perencanaan dan analisis bisnis Anda.
Gunakan kalkulator dan visualisasi berikut untuk mendukung keputusan keuangan.
""")

# Sidebar untuk pemilihan alat
tool = st.sidebar.selectbox(
    "Pilih Alat Keuangan:",
    ["Break-Even Analysis", "Cash Flow Projection", "ROI Calculator", "Loan Calculator"]
)

# Fungsi untuk menampilkan alat yang dipilih
def show_tool(tool_name):
    if tool_name == "Break-Even Analysis":
        st.header("🎯 Break-Even Analysis")
        st.markdown("""
        Break-even analysis menunjukkan berapa banyak unit yang perlu dijual atau pendapatan yang perlu dihasilkan untuk menutup biaya tetap dan variabel Anda.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fixed_cost = st.number_input("Biaya Tetap (Fixed Cost)", min_value=0, value=10000)
            price_per_unit = st.number_input("Harga per Unit", min_value=0.0, value=100.0)
            variable_cost_per_unit = st.number_input("Biaya Variabel per Unit", min_value=0.0, value=60.0)
            
        with col2:
            if price_per_unit > variable_cost_per_unit:
                break_even_units = fixed_cost / (price_per_unit - variable_cost_per_unit)
                break_even_revenue = break_even_units * price_per_unit
                
                st.metric("Break-Even Point (Units)", f"{break_even_units:.0f} units")
                st.metric("Break-Even Revenue", f"Rp {break_even_revenue:,.0f}")
                
                # Profit at different sales volumes
                units = np.arange(0, break_even_units * 2, break_even_units / 10)
                revenue = units * price_per_unit
                total_cost = fixed_cost + units * variable_cost_per_unit
                profit = revenue - total_cost
                
                # Create a dataframe for plotting
                df = pd.DataFrame({
                    'Units': units,
                    'Revenue': revenue,
                    'Total Cost': total_cost,
                    'Profit': profit
                })
                
                # Plot break-even chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=units, y=revenue, mode='lines', name='Revenue'))
                fig.add_trace(go.Scatter(x=units, y=total_cost, mode='lines', name='Total Cost'))
                fig.add_trace(go.Scatter(
                    x=[break_even_units], 
                    y=[break_even_revenue], 
                    mode='markers',
                    marker=dict(size=12, color='red'),
                    name='Break-Even Point'
                ))
                
                fig.update_layout(
                    title='Break-Even Analysis',
                    xaxis_title='Units Sold',
                    yaxis_title='Amount (Rp)',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Harga per unit harus lebih besar dari biaya variabel per unit untuk mencapai break-even point.")
        
    elif tool_name == "Cash Flow Projection":
        st.header("💸 Cash Flow Projection")
        st.markdown("""
        Proyeksikan arus kas Anda untuk beberapa bulan ke depan untuk merencanakan keuangan bisnis.
        """)
        
        # Sample data
        months = ["January", "February", "March", "April", "May", "June"]
        starting_balance = st.number_input("Saldo Awal", min_value=0, value=50000)
        
        # Create a form for inputting cash flow data
        with st.form("cash_flow_form"):
            st.subheader("Masukkan proyeksi pendapatan dan biaya bulanan")
            
            # Revenue inputs
            st.write("**Pendapatan:**")
            revenue_cols = st.columns(len(months))
            revenue = []
            
            for i, col in enumerate(revenue_cols):
                with col:
                    revenue.append(st.number_input(months[i], min_value=0, value=15000))
            
            # Expenses inputs
            st.write("**Biaya:**")
            expense_cols = st.columns(len(months))
            expenses = []
            
            for i, col in enumerate(expense_cols):
                with col:
                    expenses.append(st.number_input(months[i], min_value=0, value=10000))
                    
            submit_button = st.form_submit_button("Hitung Proyeksi Arus Kas")
        
        # Calculate cash flow
        balance = [starting_balance]
        for i in range(len(months)):
            balance.append(balance[i] + revenue[i] - expenses[i])
        
        # Create dataframe for display and plotting
        cash_flow_df = pd.DataFrame({
            'Month': ['Starting Balance'] + months,
            'Revenue': [0] + revenue,
            'Expenses': [0] + expenses,
            'Balance': balance
        })
        
        # Display dataframe
        st.dataframe(cash_flow_df.style.highlight_min(subset=['Balance'], color='red').highlight_max(subset=['Balance'], color='green'))
        
        # Create and display cash flow chart
        fig = go.Figure()
        fig.add_trace(go.Bar(x=months, y=revenue, name='Revenue', marker_color='green'))
        fig.add_trace(go.Bar(x=months, y=[-e for e in expenses], name='Expenses', marker_color='red'))
        fig.add_trace(go.Scatter(x=['Starting Balance'] + months, y=balance, mode='lines+markers', name='Balance'))
        
        fig.update_layout(
            title='Cash Flow Projection',
            xaxis_title='Month',
            yaxis_title='Amount (Rp)',
            barmode='relative',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    elif tool_name == "ROI Calculator":
        st.header("📈 ROI Calculator")
        st.markdown("""
        Kalkulator Return on Investment (ROI) untuk mengevaluasi efektivitas investasi Anda.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            investment_cost = st.number_input("Biaya Investasi", min_value=0, value=100000)
            revenue_or_savings = st.number_input("Pendapatan atau Penghematan", min_value=0, value=120000)
            time_period = st.number_input("Periode Waktu (Tahun)", min_value=1, value=1)
            
        with col2:
            roi = ((revenue_or_savings - investment_cost) / investment_cost) * 100
            annual_roi = roi / time_period
            breakeven_years = investment_cost / (revenue_or_savings / time_period) if revenue_or_savings > 0 else float('inf')
            
            st.metric("ROI Total", f"{roi:.2f}%")
            st.metric("ROI Tahunan", f"{annual_roi:.2f}%")
            
            if breakeven_years < float('inf'):
                st.metric("Waktu Balik Modal", f"{breakeven_years:.2f} tahun")
            else:
                st.metric("Waktu Balik Modal", "Tidak terbatas")
                
            # Visual indicator
            if roi > 0:
                st.success(f"Investasi ini positif dengan ROI {roi:.2f}%")
            else:
                st.error(f"Investasi ini negatif dengan ROI {roi:.2f}%")
                
        # Create projection chart
        years = np.arange(0, max(5, time_period * 2), 0.25)
        investment_values = [-investment_cost + (revenue_or_savings / time_period) * year for year in years]
        
        # Create dataframe for plotting
        df = pd.DataFrame({
            'Year': years,
            'Value': investment_values
        })
        
        # Find break-even point
        if breakeven_years < float('inf'):
            break_even_point = investment_cost / (revenue_or_savings / time_period)
        else:
            break_even_point = None
        
        # Plot ROI chart
        fig = px.line(df, x='Year', y='Value', title='Investment Value Over Time')
        
        # Add horizontal line at 0
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        # Add break-even point marker
        if break_even_point:
            fig.add_trace(go.Scatter(
                x=[break_even_point], 
                y=[0], 
                mode='markers',
                marker=dict(size=12, color='red'),
                name='Break-Even Point'
            ))
        
        fig.update_layout(
            xaxis_title='Year',
            yaxis_title='Value (Rp)',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif tool_name == "Loan Calculator":
        st.header("💳 Loan Calculator")
        st.markdown("""
        Kalkulator pinjaman untuk memperkirakan pembayaran bulanan dan total biaya pinjaman Anda.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            loan_amount = st.number_input("Jumlah Pinjaman", min_value=0, value=100000)
            interest_rate = st.number_input("Suku Bunga Tahunan (%)", min_value=0.0, value=10.0)
            loan_term_years = st.number_input("Jangka Waktu (Tahun)", min_value=1, value=5)
            
        with col2:
            # Calculate loan parameters
            monthly_interest_rate = interest_rate / 100 / 12
            loan_term_months = loan_term_years * 12
            
            # Calculate monthly payment using the formula for fixed-rate loan
            if monthly_interest_rate > 0:
                monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term_months) / ((1 + monthly_interest_rate) ** loan_term_months - 1)
            else:
                monthly_payment = loan_amount / loan_term_months
                
            total_payment = monthly_payment * loan_term_months
            total_interest = total_payment - loan_amount
            
            st.metric("Pembayaran Bulanan", f"Rp {monthly_payment:,.2f}")
            st.metric("Total Pembayaran", f"Rp {total_payment:,.2f}")
            st.metric("Total Bunga", f"Rp {total_interest:,.2f}")
        
        # Create amortization schedule
        remaining_balance = loan_amount
        principal_payments = []
        interest_payments = []
        balance_remaining = []
        
        for month in range(1, loan_term_months + 1):
            interest_payment = remaining_balance * monthly_interest_rate
            principal_payment = monthly_payment - interest_payment
            remaining_balance -= principal_payment
            
            principal_payments.append(principal_payment)
            interest_payments.append(interest_payment)
            balance_remaining.append(remaining_balance)
        
        # Create amortization chart
        months = list(range(1, loan_term_months + 1))
        
        # Create a DataFrame for the amortization data
        amort_df = pd.DataFrame({
            'Month': months,
            'Principal': principal_payments,
            'Interest': interest_payments,
            'Balance': balance_remaining
        })
        
        # Plot stacked bar chart for principal and interest payments
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=months, y=principal_payments, name='Principal', marker_color='blue'))
        fig1.add_trace(go.Bar(x=months, y=interest_payments, name='Interest', marker_color='red'))
        
        fig1.update_layout(
            title='Monthly Payment Breakdown',
            xaxis_title='Month',
            yaxis_title='Amount (Rp)',
            barmode='stack',
            height=400
        )
        
        # Plot line chart for remaining balance
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=months, y=balance_remaining, mode='lines', name='Remaining Balance'))
        
        fig2.update_layout(
            title='Remaining Loan Balance',
            xaxis_title='Month',
            yaxis_title='Balance (Rp)',
            height=400
        )
        
        # Display charts
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Display amortization table (first 12 months and last 12 months)
        if loan_term_months > 24:
            st.subheader("Jadwal Amortisasi (12 bulan pertama & terakhir)")
            amort_head = amort_df.head(12)
            amort_tail = amort_df.tail(12)
            amort_display = pd.concat([amort_head, amort_tail])
            st.dataframe(amort_display.style.format({
                'Principal': 'Rp {:,.2f}',
                'Interest': 'Rp {:,.2f}',
                'Balance': 'Rp {:,.2f}'
            }))
        else:
            st.subheader("Jadwal Amortisasi")
            st.dataframe(amort_df.style.format({
                'Principal': 'Rp {:,.2f}',
                'Interest': 'Rp {:,.2f}',
                'Balance': 'Rp {:,.2f}'
            }))

# Tampilkan alat yang dipilih
try:
    show_tool(tool)
except Exception as e:
    logger.error(f"Error displaying financial tool: {str(e)}")
    st.error(f"⚠️ Terjadi kesalahan saat menampilkan alat keuangan: {str(e)}")

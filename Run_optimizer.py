import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode
from pulp import LpProblem, LpVariable, lpSum, LpMinimize
st.set_page_config(layout="wide", page_title="LCOS and LCOE Calculator")
import matplotlib.pyplot as plt


# Title Section
st.title("LCOS and LCOE Calculator")

# Dropdown (Combo Box) for Technology Selection
technology = st.selectbox("Select Technology", ["Solar", "Wind", "Hybrid"])

# Display selected technology
st.write(f"You selected: {technology}")

# Sample Data for General Inputs
data = {
    "Parameter": [
        "System Capital Cost (Per KW)",
        "Capital Subsidy (Per KW)",
        "Plant Size (KW)",
        "Project Life of Plant (Years)",
        "Capacity Utilization Factor (%)",
        "Auxiliary Consumption (%)",
        "Discount Rate (%)",
        "Equity (%)",
        "Return on Equity (%)",
        "Loan Tenure (years)",
        "Moratorium (years)",
        "Interest on Loan (%)",
        "Operation and Maintenance Expenses in year 1 (%)",
        "Annual increase in Operation and Maintenance expenses (%)",
        "Insurance(%) of depreciated asset value)",
        "Working Capital - O & M (months)",
        "Working Capital - Receivables (months)",
        "Interest on Working Capital (%)",
        "n1 years",
        "Depreciation rate for the first n1 years (%)",
        "Percentage of capital cost on which depreciation applies (%)",
        "Annual Solar Panel Degradation (%)",
	"Grid Availability Factor (%)",
    ],
    "Solar": [40000, 0, 50,  25, 100, 0, 8, 30,1, 10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 100, 0,100],
    "Wind":  [50000, 0, 100, 25, 100, 0, 0, 30,1, 10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 100, 0,100],
    "BESS":  [20000, 0, 100, 25, 100, 0, 0, 30, 1, 10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 100, 0,100],
}

# Create tabs for General Inputs, General Outputs, and RE LCOE Calculation
tab1, tab2, tab3 , tab4, tab5,tab6,tab7= st.tabs(["General Inputs", "General Outputs", "RE LCOE Calculation","Debt, Working Capital, and Asset Value", "Battery Storage Inputs","LCOS Calculation","Battery Optimization"])


# General Inputs Section in the first tab
with tab1:
    st.subheader("General Inputs")


# Upload Hourly Demand Data
st.sidebar.subheader("Upload Hourly Demand Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

#Process uploaded file

if uploaded_file:
    # Read uploaded file
    demand_data = pd.read_csv(uploaded_file)

    # Validate datetime format for the 'Hour' column
    try:
        demand_data["Hour"] = pd.to_datetime(demand_data["Hour"])
        st.write("Hour column successfully parsed as datetime.")
    except Exception as e:
        st.error(f"Error parsing Hour column as datetime: {e}")

    st.subheader("Uploaded Hourly Demand Data")
    st.dataframe(demand_data)

    # Ensure data has necessary structure
    if "Hour" in demand_data.columns and "Demand" in demand_data.columns:
        # Optimization Problem
        st.subheader("Optimization Problem for Generation Capacity")

       # Fetch Solar and Wind CUF from General Inputs Tab
        st.sidebar.subheader("General Inputs")
        
        solar_cuf = updated_df.loc[4, "Solar"] / 100  # Convert percentage to decimal
        wind_cuf = updated_df.loc[4, "Wind"] / 100  # Convert percentage to decimal
    
    # Display the extracted CUF values in the sidebar
        st.sidebar.write(f"Solar CUF: {solar_cuf:.2%}")
        st.sidebar.write(f"Wind CUF: {wind_cuf:.2%}")
       
        total_hours = len(demand_data)

        # Define LP Problem
        prob = LpProblem("Generation_Capacity_Optimization", LpMinimize)

        # Decision Variables
        solar_capacity = LpVariable("Solar_Capacity", lowBound=0)
        wind_capacity = LpVariable("Wind_Capacity", lowBound=0)

        # Objective Function: Minimize installed capacity
        prob += solar_capacity + wind_capacity, "Total_Capacity"

        # Constraints: Meet hourly demand
        for i in range(total_hours):
            prob += (
                solar_capacity * solar_cuf + wind_capacity * wind_cuf >= demand_data["Demand"][i]
            ), f"Demand_Constraint_{i}"

        # Solve LP Problem
        prob.solve()

        # Output Results
        st.write(f"Optimal Solar Capacity: {solar_capacity.varValue:.2f} MW")
        st.write(f"Optimal Wind Capacity: {wind_capacity.varValue:.2f} MW")

        # Visualize Results
        st.subheader("Visualization")
        demand_data["Solar_Generation"] = solar_capacity.varValue * solar_cuf
        demand_data["Wind_Generation"] = wind_capacity.varValue * wind_cuf
        demand_data["Total_Generation"] = demand_data["Solar_Generation"] + demand_data["Wind_Generation"]

        st.line_chart(demand_data[["Demand", "Total_Generation"]])
    else:
        st.error("Uploaded file must contain 'Hour' and 'Demand' columns.")


    # Create a DataFrame for inputs
    df = pd.DataFrame(data)

    # Display editable table using AgGrid
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True)  # Make all columns editable
    gb.configure_column("Parameter", editable=False)  # Disable editing for the Parameter column
    grid_options = gb.build()

    # Display the AgGrid table and capture user edits
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode="MODEL_CHANGED",
        fit_columns_on_grid_load=True,
        height=650,
        width="100%",
        reload_data=False,
    )

    # Get the updated DataFrame
    updated_df = pd.DataFrame(grid_response["data"]).reset_index(drop=True)








# General Outputs Section in the second tab
with tab2:
    st.subheader("General Outputs")

    if st.button("Calculate LCOE and Outputs"):
        # Extract values from the updated DataFrame
        solar_capital_cost = updated_df.loc[0, "Solar"]
        wind_capital_cost = updated_df.loc[0, "Wind"]
        solar_plant_size = updated_df.loc[2, "Solar"]
        wind_plant_size = updated_df.loc[2, "Wind"]
        solar_subsidy = updated_df.loc[1, "Solar"]
        wind_subsidy = updated_df.loc[1, "Wind"]
        solar_equity_percentage = updated_df.loc[7, "Solar"]
        wind_equity_percentage = updated_df.loc[7, "Wind"]
        solar_dep_cap_percentage = updated_df.loc[20, "Solar"]
        wind_dep_cap_percentage = updated_df.loc[20, "Wind"]
        wind_dep_r_first_n1year = updated_df.loc[19, "Wind"]
        solar_dep_r_first_n1year = updated_df.loc[19, "Solar"]

        bess_dep_r_first_n1year = updated_df.loc[19, "BESS"]
        bess_dep_cap_percentage = updated_df.loc[20, "BESS"]

        bess_capital_cost = updated_df.loc[0, "BESS"]
        bess_plant_size = updated_df.loc[2, "BESS"]
        bess_subsidy = updated_df.loc[1, "BESS"]
        bess_equity_percentage = updated_df.loc[7, "BESS"]

       # BESS Calculations
        bess_gross_capital_cost = bess_capital_cost * bess_plant_size
        bess_subsidy_cost = bess_subsidy * bess_plant_size
        bess_net_capital_cost = bess_gross_capital_cost - bess_subsidy_cost
        bess_equity = (bess_equity_percentage / 100) * bess_gross_capital_cost
        bess_debt = bess_net_capital_cost - bess_equity

        # Calculations for General Outputs
        solar_gross_capital_cost = solar_capital_cost * solar_plant_size
        wind_gross_capital_cost = wind_capital_cost * wind_plant_size

        solar_subsidy_cost = solar_subsidy*solar_plant_size
        wind_subsidy_cost = wind_subsidy*wind_plant_size 

        solar_net_capital_cost = solar_gross_capital_cost - solar_subsidy_cost
        wind_net_capital_cost = wind_gross_capital_cost - wind_subsidy_cost

        solar_equity = (solar_equity_percentage / 100) * solar_gross_capital_cost 
        wind_equity = (wind_equity_percentage / 100) * wind_gross_capital_cost 

        solar_debt = solar_net_capital_cost - solar_equity
        wind_debt = wind_net_capital_cost - wind_equity

        wind_dep_first_nyeargrosscapex = wind_gross_capital_cost * (wind_dep_cap_percentage/100)  
        solar_dep_first_nyeargrosscapex = solar_gross_capital_cost * (solar_dep_cap_percentage /100)

        bess_dep_first_nyeargrosscapex = bess_gross_capital_cost * (bess_dep_cap_percentage /100)        


        solar_depreciation_n1 = solar_dep_first_nyeargrosscapex  * (solar_dep_r_first_n1year/100)  # Example: 10% depreciation
        wind_depreciation_n1 = wind_dep_first_nyeargrosscapex  * (wind_dep_r_first_n1year/100) #Depreciation rate for the first n1 years (%)

        bess_depreciation_n1 = bess_dep_first_nyeargrosscapex  * (bess_dep_r_first_n1year/100) #Depreciation rate for the first n1 years (%)
        

        solar_dep_firstn1_netcapex = ((solar_net_capital_cost * (wind_dep_cap_percentage/100)) * (solar_dep_r_first_n1year/100))
        wind_dep_firstn1_netcapex = (wind_net_capital_cost * (wind_dep_cap_percentage/100)) * (wind_dep_r_first_n1year/100)

        bess_dep_firstn1_netcapex = (bess_net_capital_cost * (bess_dep_cap_percentage/100)) * (bess_dep_r_first_n1year/100)
        

  
        # Create a DataFrame for General Outputs
        output_data = {
            "General Output": [
                "Gross Capital Cost",
                "Net Capital Cost",
                "Equity",
                "Debt",
                "Annual Depreciation for first n1 years (on gross capex)",
                "Annual Depreciation for after n1 years (on gross capex)",
                "Annual Depreciation for first n1 years (on net capex)",
                "Annual Depreciation for after n1 years (on net capex)",
            ],
            "Unit": ["INR", "INR", "INR", "INR", "INR", "INR", "INR", "INR"],
            "Solar Value": [
                solar_gross_capital_cost,
                solar_net_capital_cost,
                solar_equity,
                solar_debt,
                solar_depreciation_n1,
                0,  # Placeholder for after n1 years
                solar_dep_firstn1_netcapex,
                0,  # Placeholder for after n1 years
            ],
            "Wind Value": [
                wind_gross_capital_cost,
                wind_net_capital_cost,
                wind_equity,
                wind_debt,
                wind_depreciation_n1,
                0,  # Placeholder for after n1 years
                wind_dep_firstn1_netcapex,
                0,  # Placeholder for after n1 years
            ],
            "BESS Value": [
                bess_gross_capital_cost ,
                bess_net_capital_cost,
                bess_equity,
                bess_debt,
                bess_depreciation_n1,
                0,  # Placeholder for after n1 years
                bess_dep_firstn1_netcapex,
                0,  # Placeholder for after n1 years
            ],
        }

        output_df = pd.DataFrame(output_data)

        # Display General Outputs as a table
        st.table(output_df)

# RE LCOE Calculation Section in the third tab
with tab3:
    st.subheader("RE LCOE Calculation")

    plant_life = 25  # Example plant life in years

    # Data for RE LCOE Calculation
    parameters = {
        "Cost of Generation": [
            "Gross generation / kWh input (for Storage)",
            "Net generation / kWh input (for Storage)",
            "Operation and maintenance expenses",
            "Insurance",
            "Depreciation (on gross capital cost)",
            "Depreciation (on net capital cost)",
            "Interest on Term loan",
            "Interest on Working capital",
            "Return on Equity",
            "Total Cost of Generation",
            "Cost of Generation per kWh",
            "Discount factor",
            "Present value",
            "Levelised cost of generation",
            "Average cost of generation",
        ],
        "Debt": [
            "Debt opening balance",
            "Debt repayment",
            "Debt closing balance",
            "Interest",
            "Total debt service",
        ],
        "Working Capital": [
            "Operation and maintenance wcap",
            "Interest on Working capital - O&M",
            "Receivables wcap",
            "Interest on receivables wcap",
        ],
        "Financials": [
            "Cash Flow",
            "Equity IRR",
            "Cumulative Cash Flow",
            "Asset value",
        ],
    }

    if st.button("Calculate RE LCOE"):
        st.write("Performing calculations for RE LCOE...")
        # Extract necessary inputs from updated_df - General Inputs tab section
        solar_plant_size = updated_df.loc[2, "Solar"]
        wind_plant_size = updated_df.loc[2, "Wind"]

        bess_plant_size = updated_df.loc[2, "BESS"]
        
        solar_cuf = updated_df.loc[4, "Solar"] / 100    # Convert percentage to decimal - Capacity util factor
        wind_cuf = updated_df.loc[4, "Wind"] / 100
        bess_cuf = updated_df.loc[4, "BESS"] / 100

        solar_gaf = updated_df.loc[22, "Solar"] / 100 # Assuming 100% Grid Availability Factor
        wind_gaf = updated_df.loc[22, "Wind"] / 100

        bess_gaf = updated_df.loc[22, "BESS"] / 100


        wind_onm_exp_y1 = updated_df.loc[12, "Wind"] / 100
        solar_onm_exp_y1 = updated_df.loc[12, "Solar"] / 100

        bess_onm_exp_y1 = updated_df.loc[12, "Solar"] / 100

        solar_capital_cost = updated_df.loc[0, "Solar"]
        wind_capital_cost = updated_df.loc[0, "Wind"]
        
        bess_capital_cost = updated_df.loc[0, "BESS"]
        

        wind_insurance = updated_df.loc[14, "Wind"] /100
        solar_insurance = updated_df.loc[14, "Solar"] /100

        bess_insurance = updated_df.loc[14, "BESS"] /100        


        wind_dep_slm_yly = updated_df.loc[19, "Wind"]/100
        solar_dep_slm_yly = updated_df.loc[19, "Solar"] /100

        bess_dep_slm_yly = updated_df.loc[19, "BESS"] /100

        solar_subsidy = updated_df.loc[1, "Solar"]
        wind_subsidy = updated_df.loc[1, "Wind"]

        bess_subsidy = updated_df.loc[1, "BESS"]



        wind_int_loan = updated_df.loc[11, "Wind"] /100
        solar_int_loan = updated_df.loc[11, "Solar"] / 100

        bess_int_loan = updated_df.loc[11, "BESS"] / 100


        solar_equity_percentage = updated_df.loc[7, "Solar"]
        wind_equity_percentage = updated_df.loc[7, "Wind"]

        bess_equity_percentage = updated_df.loc[7, "BESS"]


        wind_wc_int = updated_df.loc[17, "Wind"] / 100
        solar_wc_int = updated_df.loc[17, "Solar"] / 100

        bess_wc_int = updated_df.loc[17, "BESS"] / 100
       

        wind_roe = updated_df.loc[8, "Wind"] / 100
        solar_roe = updated_df.loc[8, "Solar"] / 100
        bess_roe = updated_df.loc[8, "BESS"] / 100

        solar_discount_rate = updated_df.loc[6, "Solar"] / 100  # Discount rate from inputs
        wind_discount_rate = updated_df.loc[6, "Wind"] / 100  # Discount rate from inputs

        bess_discount_rate = updated_df.loc[6, "BESS"] / 100  # Discount rate from inputs

        auxiliary_consumption_solar = updated_df.loc[5, "Solar"] / 100  if not pd.isnull(updated_df.loc[5, "Solar"]) else 0 # For Solar
        auxiliary_consumption_wind = updated_df.loc[5, "Wind"] / 100  if not pd.isnull(updated_df.loc[5, "Wind"]) else 0 # For Wind

        auxiliary_consumption_bess = updated_df.loc[5, "BESS"] / 100  if not pd.isnull(updated_df.loc[5, "BESS"]) else 0 # For BESS

        
        
               

    # Calculate Gross Generation
        gross_generation = ((solar_plant_size * solar_cuf * solar_gaf * 8760) + (wind_plant_size * wind_cuf * wind_gaf * 8760))
        #net_generation = ((solar_plant_size * solar_cuf * solar_gaf * 8760) + (wind_plant_size * wind_cuf * wind_gaf * 8760))
        auxiliary_consumption = auxiliary_consumption_wind + auxiliary_consumption_solar 
        net_generation = gross_generation * (1 -  auxiliary_consumption)
        total_solar_onm_exp_y1 = ((solar_capital_cost * solar_plant_size)  * solar_onm_exp_y1)
        total_wind_onm_exp_y1 =  ((wind_capital_cost * wind_plant_size ) * wind_onm_exp_y1)

        total_bess_onm_exp_y1 =  ((bess_capital_cost * bess_plant_size ) * bess_onm_exp_y1)


        total_solar_insurance = ((solar_capital_cost * solar_plant_size)  * wind_insurance)
        total_wind_insurance =  ((wind_capital_cost * wind_plant_size) * solar_insurance)

        total_bess_insurance =  ((bess_capital_cost * bess_plant_size) * bess_insurance)
        
     
        total_onm_exp_y1 = total_solar_onm_exp_y1 + total_wind_onm_exp_y1 + total_bess_onm_exp_y1 

        dep_on_grosscapex = (((solar_capital_cost * solar_plant_size)  * solar_dep_slm_yly) + ((wind_capital_cost * wind_plant_size ) * wind_dep_slm_yly) + ((bess_capital_cost * bess_plant_size)  * bess_dep_slm_yly))

        dep_on_netcapex = ((((solar_capital_cost - solar_subsidy) * solar_plant_size)  * solar_dep_slm_yly) + (((wind_capital_cost-wind_subsidy)  * wind_plant_size ) * wind_dep_slm_yly) + (((bess_capital_cost-bess_subsidy)  * bess_plant_size ) * bess_dep_slm_yly))


        solar_tl_capital_cost = solar_capital_cost * solar_plant_size
        wind_tl_capital_cost = wind_capital_cost * wind_plant_size

        bess_tl_capital_cost = bess_capital_cost * bess_plant_size


        solar_sl_subsidy_cost = solar_subsidy*solar_plant_size
        wind_sl_subsidy_cost = wind_subsidy*wind_plant_size

        bess_sl_subsidy_cost = bess_subsidy*bess_plant_size


        solar_tl_net_capital_cost = solar_tl_capital_cost  - solar_sl_subsidy_cost 
        wind_tl_net_capital_cost = wind_tl_capital_cost - wind_sl_subsidy_cost
        
        bess_tl_net_capital_cost = bess_tl_capital_cost - bess_sl_subsidy_cost
 

        solar_tl_equity = (solar_equity_percentage / 100) * solar_tl_capital_cost
        wind_tl_equity = (wind_equity_percentage / 100) * wind_tl_capital_cost

        bess_tl_equity = (bess_equity_percentage / 100) * bess_tl_capital_cost


        total_insurance = ((wind_tl_capital_cost * wind_insurance) + (solar_tl_capital_cost  * solar_insurance)+ (bess_tl_capital_cost  * bess_insurance))  

      
        solar_tl_debt = solar_tl_net_capital_cost  - solar_tl_equity
        wind_tl_debt = wind_tl_net_capital_cost  - wind_tl_equity
        bess_tl_debt = bess_tl_net_capital_cost  - bess_tl_equity


        total_debt = solar_tl_debt + wind_tl_debt + bess_tl_debt 

        solar_tl_int = solar_tl_debt * solar_int_loan
        wind_int_loan = wind_tl_debt * wind_int_loan

        bess_int_loan = bess_tl_debt * bess_int_loan 


        int_tl = solar_tl_int + wind_int_loan + bess_int_loan 

        tot_int_wc = wind_wc_int + solar_wc_int 
        int_wc = (solar_onm_exp_y1 / 12) * tot_int_wc
        tot_roe_cost = ((solar_tl_equity * solar_roe) + (wind_tl_equity * wind_roe ) + (bess_tl_equity * bess_roe ))
        tot_gen_cost = (total_onm_exp_y1 + total_insurance + dep_on_grosscapex + int_tl)
        cost_gen_perkwh = (tot_gen_cost / net_generation)
        wind_discount_factors = [float(round(1 / ((1 + wind_discount_rate) ** year), 4)) for year in range(1, plant_life + 1)]

        solar_discount_factors = [float(round(1 / ((1 + solar_discount_rate) ** year), 4)) for year in range(1, plant_life + 1)]
        bess_discount_factors = [float(round(1 / ((1 + bess_discount_rate) ** year), 4)) for year in range(1, plant_life + 1)]
        

       
        #st.dataframe(df_lcoe)

        # Create a DataFrame for the year-wise calculations
        lcoe_data = {
        "Year": [f"Year {i+1}" for i in range(plant_life)],
        "Gross Generation (kWh)": [gross_generation] * plant_life,
        "Net Generation (kWh)": [net_generation] * plant_life,
        "O&M Expenses (INR)": [total_onm_exp_y1] * plant_life,
        "Insurance (INR)": [total_insurance] * plant_life,
        "Depreciation (Gross Capex) (INR)": [dep_on_grosscapex] * plant_life,
        "Interest on Term Loan (INR)": [int_tl] * plant_life,
        "Interest on WC (INR)": [int_wc] * plant_life,
        "Return on Equity (INR)": [tot_roe_cost] * plant_life,
        "Total Cost (INR)": [tot_gen_cost] * plant_life,
        "Discount Factor": wind_discount_factors,
        "Discounted Cost (INR)": [tot_gen_cost * discount for discount in wind_discount_factors],
        "Discounted Net Generation (kWh)": [net_generation * discount for discount in wind_discount_factors],
        }

        # Convert the dictionary to a DataFrame
        df_lcoe_yearly = pd.DataFrame(lcoe_data)
        
        # Display the year-wise calculations
        st.subheader("Yearly LCOE Calculations")
        st.dataframe(df_lcoe_yearly)
        # Calculate Present Values (PV)
        pv_total_cost = df_lcoe_yearly["Discounted Cost (INR)"].sum()
        pv_net_generation = df_lcoe_yearly["Discounted Net Generation (kWh)"].sum()

        # Calculate LCOE
        lcoe = pv_total_cost / pv_net_generation

        # Display Final LCOE
        st.subheader("Levelized Cost of Electricity (LCOE)")
        st.write(f"Levelized Cost of Electricity (LCOE): {lcoe:.4f} INR/kWh")

# Add a new tab for Debt, Working Capital, and Asset Value
#tab4 = st.tabs(["General Inputs", "General Outputs", "RE LCOE Calculation", "Debt, Working Capital, and Asset Value"])[3]

# Debt, Working Capital, and Asset Value Section
with tab4:
    st.subheader("Debt, Working Capital, and Asset Value")

    # Calculate necessary parameters for Debt
    solar_tl_net_capital_cost = updated_df.loc[2, "Solar"] * updated_df.loc[0, "Solar"] - (updated_df.loc[1, "Solar"] * updated_df.loc[2, "Solar"])
    wind_tl_net_capital_cost = updated_df.loc[2, "Wind"] * updated_df.loc[0, "Wind"] - (updated_df.loc[1, "Wind"] * updated_df.loc[2, "Wind"])

    bess_tl_net_capital_cost = updated_df.loc[2, "BESS"] * updated_df.loc[0, "BESS"] - (updated_df.loc[1, "BESS"] * updated_df.loc[2, "BESS"])


    solar_equity = (updated_df.loc[7, "Solar"] / 100) * solar_tl_net_capital_cost
    wind_equity = (updated_df.loc[7, "Wind"] / 100) * wind_tl_net_capital_cost
    bess_equity = (updated_df.loc[7, "BESS"] / 100) * bess_tl_net_capital_cost


    solar_tl_debt = solar_tl_net_capital_cost - solar_equity
    wind_tl_debt = wind_tl_net_capital_cost - wind_equity

    bess_tl_debt = bess_tl_net_capital_cost - bess_equity

    total_debt = solar_tl_debt + wind_tl_debt + bess_tl_debt   # Total debt calculation
    
    # Opening Balance for Debt (use wind or solar net capital cost as examples)
    opening_balance = total_debt  # Set dynamically based on calculated Wind net capital cost

    repayment_wind = total_debt / updated_df.loc[9, "Wind"]  # Divide total by loan tenure
    repayment_solar = total_debt / updated_df.loc[9, "Solar"]  # Divide total by loan tenure
    repayment_bess = total_debt / updated_df.loc[9, "BESS"]  # Divide total by loan tenure
 

    #repayment = total_debt / updated_df.loc[9, "Wind"]  # Divide total by loan tenure

    repayment = repayment_wind + repayment_solar + repayment_bess

    interest_rate = (updated_df.loc[11, "Wind"] + updated_df.loc[11, "Solar"] + updated_df.loc[11, "BESS"] ) / 100 # Interest rate as percentage from input

    # Initialize Debt Section Data
    debt_data = {
        "Year": [],
        "Opening Balance (INR)": [],
        "Repayment (INR)": [],
        "Closing Balance (INR)": [],
        "Interest (INR)": [],
        "Total Debt Service (INR)": [],
    }
    balance = opening_balance

    # Calculate the repayment amount and loan tenure dynamically

    # Loan tenure and interest rate
    loan_tenure = int(updated_df.loc[9, "Wind"])  # Loan tenure in years
    #interest_rate = updated_df.loc[11, "Wind"] / 100  + updated_df.loc[11, "Solar"] / 100

    interest_rate = (updated_df.loc[11, "Wind"] + updated_df.loc[11, "Solar"] + updated_df.loc[11, "BESS"]) / 100


    # Initial balance and repayment

    repayment = round(total_debt  / loan_tenure, 2)  # Fixed repayment for each year
    interest_rate = updated_df.loc[11, "Wind"] / 100  + updated_df.loc[11, "Solar"] / 100

    interest_rate = (updated_df.loc[11, "Wind"] + updated_df.loc[11, "Solar"] + updated_df.loc[11, "BESS"]) / 100


    for year in range(1, int(updated_df.loc[3, "Wind"]) + 1):  # Loop through plant life years
        interest = round(balance * interest_rate, 2)
        closing_balance = max(balance - repayment, 0)
        total_debt_service = repayment + interest

        debt_data["Year"].append(f"Year {year}")
        debt_data["Opening Balance (INR)"].append(balance)
        debt_data["Repayment (INR)"].append(repayment if balance > repayment else balance)
        debt_data["Closing Balance (INR)"].append(closing_balance)
        debt_data["Interest (INR)"].append(interest)
        debt_data["Total Debt Service (INR)"].append(total_debt_service)

        balance = closing_balance

    debt_df = pd.DataFrame(debt_data)

    # Working Capital Section
    o_and_m = round(wind_tl_net_capital_cost * (updated_df.loc[12, "Wind"] / 100), 2)  # O&M cost based on input percentage
    receivables = round(wind_tl_net_capital_cost * (updated_df.loc[16, "Wind"] / 12), 2)  # Receivables as months
    wc_interest_rate = updated_df.loc[17, "Wind"] / 100  # Interest rate on working capital

    working_capital_data = {
        "Year": [],
        "O&M WC (INR)": [],
        "Receivables WC (INR)": [],
        "Interest on WC (INR)": [],
    }

    for year in range(1, int(updated_df.loc[3, "Wind"]) + 1):  # Loop through plant life years
        interest_wc = round((o_and_m + receivables) * wc_interest_rate, 2)

        working_capital_data["Year"].append(f"Year {year}")
        working_capital_data["O&M WC (INR)"].append(o_and_m)
        working_capital_data["Receivables WC (INR)"].append(receivables)
        working_capital_data["Interest on WC (INR)"].append(interest_wc)

    wc_df = pd.DataFrame(working_capital_data)

    # Asset Value Section
    initial_asset_value = wind_tl_net_capital_cost  # Asset value starts as the net capital cost
    annual_dep_rate = (updated_df.loc[19, "Wind"]  + updated_df.loc[19, "Solar"] + updated_df.loc[19, "BESS"]) / 100
    #annual_depreciation = round(initial_asset_value * ((updated_df.loc[19, "Wind"] / 100), 2)+((updated_df.loc[19, "Wind"] / 100), 2))
    annual_depreciation = round(initial_asset_value,2) * annual_dep_rate 
    # Depreciation rate

    asset_value_data = {"Year": [], "Asset Value (INR)": []}
    asset_value = initial_asset_value

    for year in range(1, int(updated_df.loc[3, "Wind"]) + 1):  # Loop through plant life years
        asset_value_data["Year"].append(f"Year {year}")
        asset_value_data["Asset Value (INR)"].append(asset_value)
        asset_value = max(asset_value - annual_depreciation, 0)

    asset_df = pd.DataFrame(asset_value_data)

# Display DataFrames in the new tab
    st.subheader("Debt Section")
    st.dataframe(debt_df)

    st.subheader("Working Capital Section")
    st.dataframe(wc_df)

    st.subheader("Asset Value Section")
    st.dataframe(asset_df)

# Storage Inputs Section in the new tab to capture battery storage input information
with tab5:
    st.subheader("Battery Storage - Inputs")

    # Sample data for storage-related inputs
    storage_data = {
        "Parameter": [
            "Battery pack capital cost per kWh in current year (INR/kWh)",
            "Battery pack capital cost per kWh in base year (INR/kWh)",
            "Capital subsidy per kWh (%)",
            "Cost for storage container and others (INR/kWh)",
            "EPC Cost (INR/kWh)",
            "Battery Power Capacity (kW)",
            "Storage duration (E to P ratio) at 100% DoD (hr)",
            "Storage Roundtrip Efficiency (%)",
            "Depth of Discharge (%)",
            "Storage cycles per year at given DoD (cycles)",
            "End of life capacity relative to initial capacity (%)",
            "Storage cycle life (cycles)",
            "Storage shelf life (years)",
            "Cycle degradation (%)",
            "Time degradation (%)",
            "Excess solar/wind generation available for storage"
            ,
        ],
        "Unit": ["INR/kWh", "INR/kWh","%", "INR/kWh", "INR/kWh","kW", "hr", "%", "%","cycles/year", "%","cycles","INR/kWh", "years", "%", "%"],
        "Value": [20000, 20000, 10, 2500, 600, 5, 4,97,80,730,80,4000,13,0,0,1],
        
    }

    # Create a DataFrame for Storage Inputs
    storage_df = pd.DataFrame(storage_data)

    # Display editable table using AgGrid
    gb_storage = GridOptionsBuilder.from_dataframe(storage_df)
    gb_storage.configure_default_column(editable=True)  # Make all columns editable
    gb_storage.configure_column("Parameter", editable=False)  # Disable editing for the Parameter column
    gb_storage.configure_column("Unit", editable=False)  # Disable editing for the Unit column
    grid_options_storage = gb_storage.build()

    # Display the AgGrid table and capture user edits
    grid_response_storage = AgGrid(
        storage_df,
        gridOptions=grid_options_storage,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode="MODEL_CHANGED",
        fit_columns_on_grid_load=True,
        height=400,
        width="100%",
        reload_data=False,
    )

    # Get the updated DataFrame for storage inputs
    updated_storage_df = pd.DataFrame(grid_response_storage["data"]).reset_index(drop=True)

    # Display the updated storage inputs for confirmation
    #st.write("Updated Storage Inputs")
    #st.table(updated_storage_df)

# LCOS Calculation Section
with tab6:
    st.subheader("LCOS Calculation")

    if st.button("Calculate LCOS"):
        # Extract necessary inputs for LCOS Calculation
        batt_capital_cost = updated_storage_df.loc[0, "Value"]  # Battery pack capital cost per kWh
        storage_duration = updated_storage_df.loc[6, "Value"]  # Storage duration (hr)
        roundtrip_efficiency = updated_storage_df.loc[7, "Value"] / 100  # Roundtrip efficiency (convert % to decimal)
        depth_of_discharge = updated_storage_df.loc[8, "Value"] / 100  # Depth of Discharge (convert % to decimal)
        storage_cycles_per_year = updated_storage_df.loc[9, "Value"]  # Cycles per year
        cycle_life = updated_storage_df.loc[11, "Value"]  # Cycle life (cycles)
        o_and_m_cost = batt_capital_cost * (updated_df.loc[12, "BESS"] / 100)  # O&M cost as % of capital cost

        # Compute total energy stored over battery life
        total_energy_stored = (
            storage_cycles_per_year * depth_of_discharge * roundtrip_efficiency * cycle_life
        )

        # Compute LCOS
        lcos = (batt_capital_cost + o_and_m_cost * storage_duration) / total_energy_stored

        # Display the LCOS result
        st.write(f"Levelized Cost of Storage (LCOS): {lcos:.2f} INR/kWh")

# Battery Optimization
with tab7:
    st.subheader("Battery Optimization")



    # Upload generation data
    st.sidebar.subheader("Upload Generation Data")
    generation_file = st.sidebar.file_uploader("Upload Generation Data CSV", type=["csv"])

    if generation_file:
        try:
            # Read and process the generation data file
            generation_data = pd.read_csv(generation_file)
            generation_data["datetime"] = pd.to_datetime(generation_data["datetime"])  # Ensure datetime format
            
            # Validate columns
            required_columns = ["datetime", "wind", "solar", "total"]
            missing_columns = [col for col in required_columns if col not in generation_data.columns]
            if missing_columns:
                st.error(f"Missing columns in the generation file: {', '.join(missing_columns)}")
                st.stop()

            # Extract data for optimization
            generation_data = generation_data.sort_values("datetime").reset_index(drop=True)
            wind_generation = generation_data["wind"].tolist()
            solar_generation = generation_data["solar"].tolist()
            total_generation = generation_data["total"].tolist()

            st.write("### Uploaded Generation Data")
            st.dataframe(generation_data)

            st.line_chart({
                "Wind Generation": wind_generation,
                "Solar Generation": solar_generation,
                "Total Generation": total_generation,
            })
        except Exception as e:
            st.error(f"Error processing generation file: {e}")
            st.stop()
    else:
        st.warning("Please upload a generation data file.")



# Sample data for storage-related inputs
    battery_opti_data = {
        "Parameter": [
            "Battery Capacity (MWh)",
            "Max Charge Rate (MW)",
            "Max Discharge Rate (MW)",
            "Initial State of Charge (MWh)",
            "Battery Degradation Rate (% per year)",
            "Penalty Multiplier",
            "Tariff (INR/MWh)",
            "Forecast Horizon (days)",
            "Contracted Capacity (MW)"
            ,
        ],
        "Unit": ["MWh", "MW", "MW", "MWh","% per year", "times", "INR/MWh", "days","MW"],
        "Value": [20,   80,   30,   10,  2,             2,       8.00, 7, 33],
        
    }    


# Create a DataFrame for Storage Inputs
    battery_optiparameter_df = pd.DataFrame(battery_opti_data)

    # Display editable table using AgGrid
    gb_storage = GridOptionsBuilder.from_dataframe(battery_optiparameter_df)
    gb_storage.configure_default_column(editable=True)  # Make all columns editable
    gb_storage.configure_column("Parameter", editable=False)  # Disable editing for the Parameter column
    gb_storage.configure_column("Unit", editable=False)  # Disable editing for the Unit column
    grid_options_storage = gb_storage.build()

    # Display the AgGrid table and capture user edits
    grid_response_storage = AgGrid(
        battery_optiparameter_df,
        gridOptions=grid_options_storage,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode="MODEL_CHANGED",
        fit_columns_on_grid_load=True,
        height=400,
        width="100%",
        reload_data=False,
    )

    # Get the updated DataFrame for storage inputs
    updated_battery_optiparameter_df = pd.DataFrame(grid_response_storage["data"]).reset_index(drop=True)

 # Perform Optimization (if generation data is available)
    if generation_file and st.button("Optimize Battery Operations"):
        st.write("Running battery optimization...")
   

# Extract necessary inputs from the updated DataFrame
    try:
        battery_capacity = updated_battery_optiparameter_df.loc[0, "Value"]  # Battery Capacity (MWh)
        charge_rate = updated_battery_optiparameter_df.loc[1, "Value"]  # Max Charge Rate (MW)
        discharge_rate = updated_battery_optiparameter_df.loc[2, "Value"]  # Max Discharge Rate (MW)
        initial_soc = updated_battery_optiparameter_df.loc[3, "Value"]  # Initial State of Charge (MWh)
        degradation_rate = updated_battery_optiparameter_df.loc[4, "Value"]  # Degradation Rate (% per year)
        penalty_multiplier = updated_battery_optiparameter_df.loc[5, "Value"]  # Penalty Multiplier
        tariff = updated_battery_optiparameter_df.loc[6, "Value"]  # Tariff (INR/MWh)
        forecast_days = int(updated_battery_optiparameter_df.loc[7, "Value"])  # Forecast Horizon (days)
        contracted_capacity = updated_battery_optiparameter_df.loc[8, "Value"]  # Contracted Capacity (MW)
    except Exception as e:
        st.error(f"Error extracting parameters: {e}")
        st.stop()


# Compute total hours based on forecast horizon
        hours = len(generation_data)

        # Define Battery Optimization Problem
        #hours = len(generation_data)
        prob = LpProblem("Battery_Storage_Optimization", LpMinimize)

        # Decision Variables
        charge = LpVariable.dicts("Charge", range(hours), 0, charge_rate)  # Charging power
        discharge = LpVariable.dicts("Discharge", range(hours), 0, discharge_rate)  # Discharging power
        soc = LpVariable.dicts("SoC", range(hours), 0, battery_capacity)  # State of Charge
        shortage = LpVariable.dicts("Shortage", range(hours), 0)  # Shortage for penalty

        # Objective: Minimize penalties
        prob += lpSum(shortage[t] * penalty_multiplier * tariff for t in range(hours)), "Total_Penalty"

        # Constraints
        for t in range(hours):
            if t == 0:
                prob += soc[t] == initial_soc + charge[t] - discharge[t], f"Initial_SoC_{t}"
            else:
                prob += soc[t] == soc[t - 1] + charge[t] - discharge[t], f"SoC_Balance_{t}"
            prob += total_generation[t] + discharge[t] + shortage[t] >= contracted_capacity, f"Contracted_Capacity_{t}"
            prob += shortage[t] >= 0, f"Non_Negative_Shortage_{t}"

        # Solve the optimization problem
        status = prob.solve()
        if status != 1:
            st.error("Optimization failed. Please check your inputs.")
            st.stop()

        # Results
        schedule_bess = pd.DataFrame({
            "Hour": range(hours),
            "Wind Generation (MW)": wind_generation,
            "Solar Generation (MW)": solar_generation,
            "Total Generation (MW)": total_generation,
            "Charge (MW)": [charge[t].varValue for t in range(hours)],
            "Discharge (MW)": [discharge[t].varValue for t in range(hours)],
            "State of Charge (MWh)": [soc[t].varValue for t in range(hours)],
            "Shortage (MW)": [shortage[t].varValue for t in range(hours)],
        })

        schedule_bess["Penalty (INR)"] = schedule["Shortage (MW)"] * penalty_multiplier * tariff

# Visualization of the Project Generation, Charge, and Discharge Schedule
        #if generation_file and "schedule" in locals():
        st.subheader("Project Generation, Charge, and Discharge Schedule")

 # Display the results
        st.write("### Optimization Results")
        st.dataframe(schedule_bess)

    # Create the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(schedule_bess["Hour"], schedule_bess["Wind Generation (MW)"], label="Wind Generation (MW)", marker='o')
        ax.plot(schedule_bess["Hour"], schedule_bess["Solar Generation (MW)"], label="Solar Generation (MW)", marker='x')
        ax.plot(schedule_bess["Hour"], schedule_bess["Charge (MW)"], label="Charge (MW)", marker='^')
        ax.plot(schedule_bess["Hour"], schedule_bess["Discharge (MW)"], label="Discharge (MW)", marker='s')
        ax.plot(schedule_bess["Hour"], schedule_bess["State of Charge (MWh)"], label="State of Charge (MWh)", linestyle='--')

    # Customize the plot
        ax.set_xlabel("Hour")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid()

    # Display the plot in Streamlit
        st.pyplot(fig)

    # Display the detailed schedule
        st.write("Detailed schedule of energy generation and battery management:")
        st.dataframe(schedule_bess)


       

        # Visualization
        st.write("### Visualization of Results")
        st.line_chart(schedule_bess[["Total Generation (MW)", "Charge (MW)", "Discharge (MW)", "State of Charge (MWh)"]])



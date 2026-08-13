import streamlit as st
import requests
from datetime import date
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000"

st.title("Expense Tracker")

categories_response = requests.get(f"{API_URL}/categories/")
categories = categories_response.json()
category_names = [c["name"] for c in categories]
category_lookup = {c["name"]: c["id"] for c in categories}
transactions_response = requests.get(f"{API_URL}/transactions/")
transactions = transactions_response.json()

if transactions:
    df = pd.DataFrame([{"date": t["date"],
                        "amount": t["amount"],
                        "description": t["description"],
                        "category": t["category"]["name"],
                        "id": t["id"]}
                        for t in transactions])
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = pd.to_numeric(df["amount"])

    months = sorted(df["date"].dt.to_period("M").unique().astype(str), reverse=True)
    selected_month = st.selectbox("Filter by month", ["All"] + months)

    if selected_month != "All":
        filtered_df = df[df["date"].dt.to_period("M").astype(str) == selected_month]
    else:
        filtered_df = df
else:
    filtered_df = pd.DataFrame()

def show_summary():
    st.subheader("This Month at a Glance")

    current_month = months[0] if months else None
    previous_month = months[1] if len(months) > 1 else None

    current_total = df[df["date"].dt.to_period("M").astype(str) == current_month]["amount"].sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        if previous_month:
            previous_total = df[df["date"].dt.to_period("M").astype(str) == previous_month]["amount"].sum()
            delta = current_total - previous_total
            st.metric("Total Spent", f"{current_total:.2f}", delta=f"{delta:+.2f}", delta_color="inverse")
        else:
            st.metric("Total Spent", f"{current_total:.2f}")

    with col2:
        current_df = df[df["date"].dt.to_period("M").astype(str) == current_month]
        if not current_df.empty:
            top_category = current_df.groupby("category")["amount"].sum().idxmax()
            top_amount = current_df.groupby("category")["amount"].sum().max()
            st.metric("Top Category", top_category, f"{top_amount:.2f}")

    with col3:
        st.metric("Transactions This Month", len(current_df) if not current_df.empty else 0)

def show_add_transaction():
    with st.expander("➕ Add Transaction"):
        with st.form("add_transaction_form"):
            transaction_date = st.date_input("Date", value=date.today())
            amount = st.number_input("Amount", min_value=0.0, step=0.01)
            description = st.text_input("Description")
            selected_category = st.selectbox("Category", category_names)

            submitted = st.form_submit_button("Add Transaction")

            if submitted:
                payload = {
                    "date": transaction_date.isoformat(),
                    "amount": amount,
                    "description": description,
                    "category_id": category_lookup[selected_category],
                }
                response = requests.post(f"{API_URL}/transactions/", json=payload)

                if response.status_code == 201:
                    st.success("Transaction added!")
                else:
                    st.error(f"Failed to add transaction: {response.text}")

def show_add_category():
    with st.expander("➕ Add New Category"):
        with st.form("add_category_form"):
            new_category_name = st.text_input("Category Name")
            category_submitted = st.form_submit_button("Add Category")

            if category_submitted:
                if new_category_name.strip() == "":
                    st.warning("Please enter a category name.")
                else:
                    response = requests.post(
                        f"{API_URL}/categories/", json={"name": new_category_name}
                    )
                    if response.status_code == 201:
                        st.success(f"Category '{new_category_name}' added!")
                        st.rerun()
                    elif response.status_code == 409:
                        st.error("That category already exists.")
                    else:
                        st.error(f"Failed to add category: {response.text}")
        if "category_added" in st.session_state:
            st.success(f"Category '{st.session_state['category_added']}' added!")
            del st.session_state["category_added"]  

def show_transactions():
    with st.expander("➕ Transactions"):
        st.subheader("Transactions")
        st.dataframe(filtered_df.drop(columns=["id"]).sort_values("date", ascending=True))
        total = filtered_df["amount"].sum()
        st.metric(f"Total spent ({selected_month})", f"{total:.2f}") 

def show_category_chart():
    with st.expander("➕ Spending by Category"):
        st.subheader("Spending by Category")
        category_totals = filtered_df.groupby("category")["amount"].sum().sort_values(ascending=False)
        comparison = df.groupby([df["date"].dt.to_period("M").astype(str), "category"])["amount"].sum().unstack(fill_value=0)
        comparison.index = pd.to_datetime(comparison.index).strftime("%b %Y")
        fig = px.bar(comparison.T,
                     barmode="stack",
                     labels={"value": "Amount", "index": "Month", "variable": "Category"},)
        fig.update_xaxes(tickangle=0)
        st.plotly_chart(fig)
        # st.bar_chart(comparison.T)
        # st.bar_chart(category_totals) 

def show_bulk_import():
    with st.expander("➕ Bulk Import Transactions"):
        import_df = pd.DataFrame(
            {
                "date": pd.Series(dtype="str"),
                "description": pd.Series(dtype="str"),
                "amount": pd.Series(dtype="float"),
                "category": pd.Series(dtype="str"),
            }
        )

        edited_df = st.data_editor(
            import_df,
            num_rows="dynamic",
            column_config={
                "date": st.column_config.TextColumn("Date (YYYY-MM-DD)"),
                "description": st.column_config.TextColumn("Description"),
                "amount": st.column_config.NumberColumn("Amount"),
                "category": st.column_config.SelectboxColumn("Category", options=category_names),
            },
            key="bulk_import_editor",
        )

        if st.button("Add All Transactions"):
            errors = []
            success_count = 0

            for i, row in edited_df.iterrows():
                if pd.isna(row["date"]) or pd.isna(row["amount"]) or pd.isna(row["category"]):
                    continue

                try:
                    parsed_date = pd.to_datetime(row["date"], dayfirst=True).date().isoformat()
                except (ValueError, TypeError):
                    errors.append(f"Row {i + 1}: invalid date '{row['date']}'")
                    continue

                payload = {
                    "date": parsed_date,
                    "amount": row["amount"],
                    "description": row["description"] if pd.notna(row["description"]) else "",
                    "category_id": category_lookup[row["category"]],
                }
                response = requests.post(f"{API_URL}/transactions/", json=payload)

                if response.status_code == 201:
                    success_count += 1
                else:
                    errors.append(f"Row {i + 1}: {response.text}")

            st.success(f"Added {success_count} transactions.")
            if errors:
                st.error("Some rows failed:\n" + "\n".join(errors))

def show_edit_delete():
    with st.expander("➕ Edit or Delete a Transaction"):
        if filtered_df.empty:
            st.info("No transactions to edit.")
            return

        options = {f"{row['date'].date()} - {row['description']} - {row['amount']}": row["id"]
                for _, row in filtered_df.reset_index().iterrows()}
        selected_label = st.selectbox("Select a transaction", list(options.keys()))
        selected_id = options[selected_label]
        selected_row = filtered_df[filtered_df["id"] == selected_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Edit**")
            new_amount = st.number_input("Amount", value=float(selected_row["amount"]), key=f"edit_amount_{selected_id}")
            new_description = st.text_input("Description", value=selected_row["description"], key=f"edit_desc_{selected_id}")
            if st.button("Save Changes"):
                response = requests.patch(
                    f"{API_URL}/transactions/{selected_id}",
                    json={"amount": new_amount, "description": new_description},
                )
                if response.status_code == 200:
                    st.success("Updated!")
                    st.rerun()
                else:
                    st.error(f"Update failed: {response.text}")

        with col2:
            st.write("**Delete**")
            st.write(f"Delete: {selected_label}")
            if st.button("Confirm Delete", type="primary"):
                response = requests.delete(f"{API_URL}/transactions/{selected_id}")
                if response.status_code == 204:
                    st.success("Deleted!")
                    st.rerun()
                else:
                    st.error(f"Delete failed: {response.text}")


sections = [
    show_summary,
    show_transactions,
    show_category_chart,
    show_add_transaction,
    show_edit_delete,
    show_add_category,
    show_bulk_import,
]

for section in sections:
    section()
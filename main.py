import gspread
import pandas as pd
import streamlit as st
from helpers.calc_dough import calc_pizza_dough

st.set_page_config(page_title='PizzaCalc', page_icon=':pizza:', layout='wide')


@st.cache_resource
def init_gspread():
    client = gspread.service_account('credentials.json')
    table = client.open('pizza_db')
    return table.worksheet('recipes')


try:
    worksheet = init_gspread()
except ConnectionError as e:
    st.error(f'Error with Google Sheet connection: {e}')
    worksheet = None

st.title('Pizza Calculator')
st.write('Dial in your size, quantity, and thickness.')
st.divider()

st.subheader('Pizza Pizza Calculator')
col1, col2, col3, col4 = st.columns(4)
with col1:
    pizza_size = st.slider('Pizza size (cm)', min_value=20, max_value=40, value=30)
with col2:
    pizza_number = st.slider('Number of pizzas', min_value=1, max_value=10, value=4)
with col3:
    hydration_number = st.slider('Hydration', min_value=1, max_value=100, value=62)
with col4:
    thickness = st.pills(
        'Thickness', ['Thin', 'Regular', 'Thick'], default='Regular', selection_mode='single'
    )

if not thickness:
    thickness = 'Regular'

ball_weight, flour, water, salt, yeast, oil, hydration, ingredients_dict = calc_pizza_dough(
    pizza_size, pizza_number, hydration_number, thickness
)

m1, m2, m3, m4 = st.columns(4)
m1.metric('DOUGH BALL', f'{ball_weight} g')
m2.metric('FLOUR', f'{flour} g')
m3.metric('WATER', f'{water} g')
m4.metric('HYDRATION', f'{hydration}%')

df_calc = pd.DataFrame(ingredients_dict)
st.dataframe(df_calc, hide_index=True, width='stretch')

st.divider()

st.subheader('Save Recipe to Database')
with st.form('save_recipe_form', clear_on_submit=True):
    recipe_name = st.text_input('Recipe Name', placeholder='e.g. Classic Neapolitan')
    submitted = st.form_submit_button('Save Recipe', width='stretch')

    if submitted:
        if not recipe_name:
            st.warning('Please enter a recipe name before saving.')
        elif worksheet is None:
            st.error('Database connection is not available.')
        else:
            row_data = [
                recipe_name,
                pizza_number,  # servings
                flour,
                water,
                salt,
                yeast,
                oil,
                hydration,
            ]
            try:
                worksheet.append_row(row_data)
                st.success(f'Recipe "{recipe_name}" saved successfully!')
                st.rerun()
            except Exception as err:
                st.error(f'Failed to save: {err}')

st.divider()

if worksheet:
    records = worksheet.get_all_records()
    df_db = pd.DataFrame(records)
else:
    df_db = pd.DataFrame()

if not df_db.empty:
    st.subheader('Search and Filter Database')

    search_term = st.text_input('Search by Recipe Name', '')

    filtered_df = df_db.copy()
    if search_term:
        filtered_df = filtered_df[
            filtered_df['recipe_name'].str.contains(search_term, case=False, na=False)
        ]

    st.dataframe(
        filtered_df,
        hide_index=True,
        width='stretch',
        column_config={
            'servings': 'Servings',
            'recipe_name': 'Recipe name',
            'flour_g': 'Flour (g)',
            'water_g': 'Water (g)',
            'salt_g': 'Salt (g)',
            'yeast_g': 'Yeast (g)',
            'olive_oil_g': 'Olive oil (g)',
            'hydration_percent': 'Hydration (%)',
        },
    )

    st.subheader('Recipe Analytics (Top & Sort)')
    display_labels = {
        'flour_g': 'Flour',
        'water_g': 'Water',
        'hydration_percent': 'Hydration percent',
    }
    sort_column = st.selectbox(
        'Sort data by:',
        options=list(display_labels.keys()),
        format_func=lambda x: display_labels[x],
    )

    sort_order = st.radio(
        'Order:',
        options=['Descending (Highest first)', 'Ascending (Lowest first)'],
        horizontal=True,
    )

    is_ascending = True if 'Ascending' in sort_order else False
    sorted_df = df_db.sort_values(by=sort_column, ascending=is_ascending)

    st.write(f'**Sorted Database by {sort_column}:**')
    st.dataframe(
        sorted_df,
        hide_index=True,
        width='stretch',
        column_config={
            'servings': 'Servings',
            'recipe_name': 'Recipe name',
            'flour_g': 'Flour (g)',
            'water_g': 'Water (g)',
            'salt_g': 'Salt (g)',
            'yeast_g': 'Yeast (g)',
            'olive_oil_g': 'Olive oil (g)',
            'hydration_percent': 'Hydration (%)',
        },
    )

    top_recipe = sorted_df.iloc[0]
    st.info(
        f'🏆 **Top Recipe according to {sort_column}:** {top_recipe["recipe_name"]} ({top_recipe[sort_column]})'
    )

    st.divider()

    st.subheader('Delete Recipe from Database')
    recipe_list = df_db['recipe_name'].tolist()
    recipe_to_delete = st.selectbox(
        'Select recipe to delete:', options=['-- Select --'] + recipe_list
    )

    if st.button('Delete Selected Recipe', type='primary'):
        if recipe_to_delete != '-- Select --':
            try:
                row_index = recipe_list.index(recipe_to_delete) + 2
                worksheet.delete_rows(row_index)
                st.success(f'Deleted "{recipe_to_delete}" successfully!')
                st.rerun()
            except Exception as err:
                st.error(f'Error deleting row: {err}')
        else:
            st.warning('Please select a recipe to delete.')

st.divider()
st.subheader('Dough making instructions')
with st.container():
    with st.status('Phase 1: Mixing & Prepping', expanded=True, state='running'):
        st.write(':orange-background[01] Room temperature water')
        st.write(':orange-background[02] Mix water and dry active yeast')
        st.write(':orange-background[03] Add flour, olive oil and mix 2 minutes')
        st.write(':orange-background[04] Add salt to taste')
        st.write(':orange-background[05] Mix 10 more minutes')

    with st.status('Phase 2: Proofing & Aging', expanded=False, state='complete'):
        st.write(':orange-background[06] Cover and rest for 1 - 3 hours')
        st.write(':orange-background[07] Shape into balls and seal')
        st.write(':orange-background[08] Refrigerate for 2 - 3 days')
        st.write(':orange-background[09] Bring to room temp before using')

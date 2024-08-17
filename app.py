import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df


population_data_path = "Всего.csv"
salary_data_path = "ЗП.csv"
men_data_path = "Мужчины.csv"
women_data_path = "Женщины.csv"

population_df = load_data(population_data_path)
salary_df = load_data(salary_data_path)
men_data_df = load_data(men_data_path)
women_data_df = load_data(women_data_path)

salary_df.columns = salary_df.columns.str.strip()

st.title('Статистика по населению и заработной плате в России')

subject = st.sidebar.selectbox('Выберите субъект Российской Федерации',
                               population_df['Субъект Российской Федерации'].unique())
min_year = population_df['Год'].min().astype(int)
max_year = population_df['Год'].max().astype(int)
year_mode = st.sidebar.radio(
    'Выберите режим выбора года', ('Один год', 'Диапазон лет'), index=1)

type_mode = st.sidebar.radio(
    'Выберите режим отображения', ('Всего', 'Мужчины', 'Женщины'))

# Определение базового набора данных
if type_mode == 'Всего':
    base_df = population_df
elif type_mode == 'Мужчины':
    base_df = men_data_df
elif type_mode == 'Женщины':
    base_df = women_data_df

# Фильтрация по субъекту и году/годам
if year_mode == 'Один год':
    selected_year = st.sidebar.slider(
        'Выберите год', min_year, max_year, min_year)
    filtered_df = base_df[(base_df['Субъект Российской Федерации'] == subject) &
                          (base_df['Год'] == selected_year)]
    filtered_salary_df = salary_df[salary_df['Год'] == selected_year]
else:
    year_range = st.sidebar.slider(
        'Выберите диапазон лет', min_year, max_year, (min_year, max_year))
    filtered_df = base_df[(base_df['Субъект Российской Федерации'] == subject) &
                          (base_df['Год'].between(year_range[0], year_range[1]))]
    filtered_salary_df = salary_df[salary_df['Год'].between(
        year_range[0], year_range[1])]

if filtered_df.empty:
    st.warning("Нет данных для выбранных параметров. Пожалуйста, измените выбор.")
else:
    if year_mode == 'Один год':
        st.header(f'Данные за {selected_year} год для {subject}')
        st.subheader('Данные по населению')
        population_display = filtered_df.reset_index(drop=True).iloc[:, 2:]
        st.write(population_display.to_html(
            index=False), unsafe_allow_html=True)

        st.subheader('Данные по заработной плате')
        salary_display = filtered_salary_df.reset_index(drop=True).iloc[:, 1:]
        st.write(salary_display.to_html(index=False), unsafe_allow_html=True)
    else:
        # График численности населения
        st.header(f'Численность населения в {subject} по годам')
        fig_population = px.line(filtered_df, x='Год', y='Всего')
        fig_population.update_xaxes(dtick=1)
        st.plotly_chart(fig_population)

        # График распределения по возрастным группам
        fig_age_groups = go.Figure()
        for column in ['моложе трудоспособного возраста', 'в трудоспособном возрасте', 'старше трудоспособного возраста']:
            if column in filtered_df.columns:
                fig_age_groups.add_trace(go.Scatter(
                    x=filtered_df['Год'], y=filtered_df[column], mode='lines', name=column))
        fig_age_groups.update_layout(
            title='Распределение населения по возрастным группам')
        fig_age_groups.update_xaxes(dtick=1)
        st.plotly_chart(fig_age_groups)

        # График распределения по возрасту
        age_columns = ["до 1 "] + [str(i) for i in range(1, 101)]
        selected_ages = st.sidebar.multiselect(
            'Выберите возрастные группы', age_columns, default=['18'])
        valid_ages = [
            age for age in selected_ages if age in filtered_df.columns]

        if valid_ages:
            age_distribution = filtered_df.melt(
                id_vars=['Год'], value_vars=valid_ages, var_name='Возраст', value_name='Количество')
            fig_age_distribution = px.line(age_distribution, x='Год', y='Количество',
                                           color='Возраст', title='Распределение населения по возрасту')
            fig_age_distribution.update_xaxes(dtick=1)
            st.plotly_chart(fig_age_distribution)
        else:
            st.warning(
                "Выберите корректные возрастные группы для отображения графика.")

        st.header(
            'Среднемесячная номинальная начисленная заработная плата работников')
        options = ['Средняя заработная плата',
                   'Заработная плата по кварталам', 'Заработная плата по месяцам']
        choice = st.sidebar.selectbox(
            'Выберите график для отображения', options)

        def create_plot(df, x, y, plot_type, title, single_year=False):
            fig = go.Figure()
            plot_types = {
                'Линейный график': go.Scatter if not single_year else go.Bar,
                'Столбчатая диаграмма': go.Bar,
                'Круговая диаграмма': go.Pie,
                'Диаграмма с областями': lambda x, y, name: go.Scatter(x=x, y=y, fill='tozeroy', name=name) if not single_year else go.Bar(x=x, y=y, name=name)
            }

            plot_func = plot_types.get(plot_type, go.Scatter)

            for yi in y:
                if plot_type == 'Круговая диаграмма':
                    fig.add_trace(
                        plot_func(labels=df[x], values=df[yi], name=yi))
                else:
                    fig.add_trace(plot_func(x=df[x], y=df[yi], name=yi))

            fig.update_layout(title=title)
            if not single_year:
                fig.update_xaxes(dtick=1)
            return fig

        plot_types = ['Линейный график', 'Столбчатая диаграмма',
                      'Круговая диаграмма', 'Диаграмма с областями']
        plot_choice = st.sidebar.selectbox(
            'Выберите тип графика', plot_types, key='plot_choice')

        single_year = year_mode == 'Один год'

        if choice == 'Средняя заработная плата':
            fig_salary = create_plot(filtered_salary_df, 'Год', [
                                     'В среднем за год'], plot_choice, 'Средняя заработная плата по годам', single_year)
            st.plotly_chart(fig_salary)

        if choice == 'Заработная плата по кварталам':
            quarters = ['I', 'II', 'III', 'IV']
            quarter_names = ['I квартал', 'II квартал',
                             'III квартал', 'IV квартал']
            selected_quarters = st.sidebar.multiselect(
                'Выберите кварталы для сравнения', quarters, default=quarters)
            fig_salary_quarters = create_plot(
                filtered_salary_df, 'Год', selected_quarters, plot_choice, 'Заработная плата по кварталам', single_year)
            st.plotly_chart(fig_salary_quarters)

        elif choice == 'Заработная плата по месяцам':
            months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                      'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
            selected_months = st.sidebar.multiselect(
                'Выберите месяцы для сравнения', months, default=months)
            fig_salary_months = create_plot(
                filtered_salary_df, 'Год', selected_months, plot_choice, 'Заработная плата по месяцам', single_year)
            st.plotly_chart(fig_salary_months)

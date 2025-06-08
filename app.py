import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

# Настройка страницы
st.set_page_config(
    page_title="Статистика России",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(0deg, #d52b1e 0%, #0039a6 50%, #ffffff 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #0039a6;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(file_path):
    """Загрузка данных с обработкой ошибок"""
    try:
        if not Path(file_path).exists():
            st.error(f"Файл {file_path} не найден!")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        # Очистка названий колонок
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Ошибка при загрузке файла {file_path}: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def get_data_summary(df, data_type):
    """Получение сводной информации о данных"""
    if df.empty:
        return {}
    
    summary = {
        'total_records': len(df),
        'years_range': f"{df['Год'].min()} - {df['Год'].max()}" if 'Год' in df.columns else "Н/Д",
        'subjects_count': len(df['Субъект Российской Федерации'].unique()) if 'Субъект Российской Федерации' in df.columns else 0,
        'data_type': data_type
    }
    return summary

def create_info_cards(summaries):
    """Создание информационных карточек"""
    cols = st.columns(len(summaries))
    
    for i, (name, summary) in enumerate(summaries.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{name}</h4>
                <p><strong>Записей:</strong> {summary.get('total_records', 0)}</p>
                <p><strong>Период:</strong> {summary.get('years_range', 'Н/Д')}</p>
                <p><strong>Субъектов:</strong> {summary.get('subjects_count', 0)}</p>
            </div>
            """, unsafe_allow_html=True)

def create_enhanced_plot(df, x, y_cols, plot_type, title, single_year=False):
    """Создание улучшенных графиков с обычными цветами"""
    if df.empty or not y_cols:
        return go.Figure().add_annotation(text="Нет данных для отображения", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Используем стандартную цветовую палитру Plotly
    colors = px.colors.qualitative.Set3
    
    if plot_type == 'Линейный график':
        fig = go.Figure()
        for i, col in enumerate(y_cols):
            if col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df[x], y=df[col], 
                    name=col, 
                    line=dict(color=colors[i % len(colors)], width=3),
                    hovertemplate=f'<b>{col}</b><br>Год: %{{x}}<br>Значение: %{{y:,.0f}}<extra></extra>'
                ))
    
    elif plot_type == 'Столбчатая диаграмма':
        fig = go.Figure()
        for i, col in enumerate(y_cols):
            if col in df.columns:
                fig.add_trace(go.Bar(
                    x=df[x], y=df[col], 
                    name=col,
                    marker_color=colors[i % len(colors)],
                    hovertemplate=f'<b>{col}</b><br>Год: %{{x}}<br>Значение: %{{y:,.0f}}<extra></extra>'
                ))
    
    elif plot_type == 'Диаграмма с областями':
        fig = go.Figure()
        for i, col in enumerate(y_cols):
            if col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df[x], y=df[col], 
                    name=col, 
                    fill='tonexty' if i > 0 else 'tozeroy',
                    fillcolor=colors[i % len(colors)],
                    line=dict(color=colors[i % len(colors)]),
                    hovertemplate=f'<b>{col}</b><br>Год: %{{x}}<br>Значение: %{{y:,.0f}}<extra></extra>'
                ))
    
    elif plot_type == 'Круговая диаграмма' and len(df) == 1:
        values = [df[col].iloc[0] for col in y_cols if col in df.columns]
        fig = go.Figure(data=[go.Pie(
            labels=y_cols, 
            values=values,
            hole=0.3,
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Значение: %{value:,.0f}<br>Процент: %{percent}<extra></extra>'
        )])
    
    else:
        fig = go.Figure()
    
    # Улучшение внешнего вида
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif", size=12),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    if not single_year and x in df.columns:
        fig.update_xaxes(
            dtick=1,
            gridcolor='lightgray',
            gridwidth=0.5,
            title_font=dict(size=14)
        )
    
    fig.update_yaxes(
        gridcolor='lightgray',
        gridwidth=0.5,
        title_font=dict(size=14)
    )
    
    return fig

def main():
    # Заголовок приложения
    st.markdown("""
    <div class="main-header">
        <h1>📊 Статистика по населению и заработной плате в России</h1>
        <p>Интерактивный анализ демографических и экономических данных</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Пути к файлам данных
    data_files = {
        "Всего": "Всего.csv",
        "Заработная плата": "ЗП.csv", 
        "Мужчины": "Мужчины.csv",
        "Женщины": "Женщины.csv"
    }
    
    # Загрузка данных
    with st.spinner('Загрузка данных...'):
        data = {}
        summaries = {}
        
        for name, path in data_files.items():
            df = load_data(path)
            data[name] = df
            if not df.empty:
                summaries[name] = get_data_summary(df, name)
    
    # Проверка наличия данных
    if all(df.empty for df in data.values()):
        st.error("❌ Не удалось загрузить данные. Проверьте наличие CSV файлов.")
        return
    
    # Боковая панель с настройками
    st.sidebar.title("⚙️ Настройки")
    
    # Выбор субъекта
    subjects = []
    for df in data.values():
        if not df.empty and 'Субъект Российской Федерации' in df.columns:
            subjects.extend(df['Субъект Российской Федерации'].unique())
    
    if not subjects:
        st.error("Не найдены данные о субъектах РФ")
        return
    
    # Фильтруем субъекты, исключая "0" и сортируем
    filtered_subjects = sorted([subj for subj in set(subjects) if str(subj) != '0'])
    
    # Определяем индекс по умолчанию для "Российская Федерация"
    default_index = 0
    if "Российская Федерация" in filtered_subjects:
        default_index = filtered_subjects.index("Российская Федерация")
    
    subject = st.sidebar.selectbox(
        '🏛️ Выберите субъект РФ',
        filtered_subjects,
        index=default_index
    )
    
    # Определение диапазона годов
    all_years = []
    for df in data.values():
        if not df.empty and 'Год' in df.columns:
            all_years.extend(df['Год'].unique())
    
    if not all_years:
        st.error("Не найдены данные о годах")
        return
    
    min_year, max_year = int(min(all_years)), int(max(all_years))
    
    # Выбор периода
    year_mode = st.sidebar.radio(
        '📅 Выберите режим выбора года', 
        ('Один год', 'Диапазон лет'), 
        index=1
    )
    
    # Выбор типа данных по населению
    type_mode = st.sidebar.radio(
        '👥 Выберите категорию населения', 
        ('Всего', 'Мужчины', 'Женщины')
    )
    
    # Определение базового набора данных
    base_df = data[type_mode]
    salary_df = data["Заработная плата"]
    
    if base_df.empty:
        st.warning(f"⚠️ Данные для категории '{type_mode}' отсутствуют")
        return
    
    # Фильтрация данных
    if year_mode == 'Один год':
        selected_year = st.sidebar.slider(
            'Выберите год', min_year, max_year, max_year
        )
        filtered_df = base_df[
            (base_df['Субъект Российской Федерации'] == subject) &
            (base_df['Год'] == selected_year)
        ]
        filtered_salary_df = salary_df[salary_df['Год'] == selected_year] if not salary_df.empty else pd.DataFrame()
    else:

        
        # Один слайдер с диапазоном
        if year_mode == 'Диапазон лет':
            st.sidebar.write('Выберите диапазон лет:')
            
            year_range = st.sidebar.slider(
                "📅 Диапазон лет",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                step=1,
                help="Перетащите края слайдера для выбора диапазона"
            )
            
            start_year, end_year = year_range
            
            # Дополнительная проверка (на случай багов в Streamlit)
            if start_year >= end_year:
                st.sidebar.error("⚠️ Начальный год должен быть меньше конечного!")
                st.stop()
        
        filtered_df = base_df[
            (base_df['Субъект Российской Федерации'] == subject) &
            (base_df['Год'].between(start_year, end_year))
        ]
        filtered_salary_df = salary_df[
            salary_df['Год'].between(start_year, end_year)
        ] if not salary_df.empty else pd.DataFrame()
    
    # Основной контент
    if filtered_df.empty:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ Нет данных</h4>
            <p>Нет данных для выбранных параметров. Попробуйте изменить настройки.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Отображение данных для одного года 
    if year_mode == 'Один год':
        st.subheader(f"👥 Население - {selected_year}")
        if not filtered_df.empty:
            population_display = filtered_df.reset_index(drop=True).iloc[:, 2:]
            st.dataframe(population_display, use_container_width=True)
        
        st.subheader(f"💰 Заработная плата - {selected_year}")
        if not filtered_salary_df.empty:
            salary_display = filtered_salary_df.reset_index(drop=True).iloc[:, 1:]
            st.dataframe(salary_display, use_container_width=True)
        else:
            st.info("Данные о заработной плате для выбранного года отсутствуют")
    
    # Отображение графиков для диапазона лет
    else:
        st.header(f'📊 Аналитика: {subject}')
        
        # График общей численности населения
        if 'Всего' in filtered_df.columns:
            fig_population = create_enhanced_plot(
                filtered_df, 'Год', ['Всего'], 
                'Линейный график', 
                f'Общая численность населения в регионе {subject}'
            )
            st.plotly_chart(fig_population, use_container_width=True)
        
        # График по возрастным группам
        age_group_cols = [
            'моложе трудоспособного возраста', 
            'в трудоспособном возрасте', 
            'старше трудоспособного возраста'
        ]
        available_age_cols = [col for col in age_group_cols if col in filtered_df.columns]
        
        if available_age_cols:
            fig_age_groups = create_enhanced_plot(
                filtered_df, 'Год', available_age_cols,
                'Диаграмма с областями',
                'Распределение населения по возрастным группам'
            )
            st.plotly_chart(fig_age_groups, use_container_width=True)
        
        # Детальное распределение по возрасту
        age_columns = ["до 1 "] + [str(i) for i in range(1, 101)]
        available_ages = [age for age in age_columns if age in filtered_df.columns]
        
        if available_ages:
            st.subheader("🎯 Детальное распределение по возрасту")
            selected_ages = st.multiselect(
                'Выберите возрастные группы для анализа',
                available_ages,
                default=['18', '25', '30', '40', '50', '60'] if any(age in available_ages for age in ['18', '25', '30', '40', '50', '60']) else available_ages[:5]
            )
            
            if selected_ages:
                fig_age_dist = create_enhanced_plot(
                    filtered_df, 'Год', selected_ages,
                    'Линейный график',
                    'Динамика численности по выбранным возрастным группам'
                )
                st.plotly_chart(fig_age_dist, use_container_width=True)
        
        # Анализ заработной платы
        if not filtered_salary_df.empty:
            st.header('💰 Анализ заработной платы')
            
            # Настройки для зарплаты
            col1, col2 = st.columns(2)
            
            with col1:
                salary_options = [
                    'Средняя заработная плата',
                    'Заработная плата по кварталам', 
                    'Заработная плата по месяцам'
                ]
                choice = st.selectbox('Выберите анализ', salary_options)
            
            with col2:
                plot_types = [
                    'Линейный график', 
                    'Столбчатая диаграмма',
                    'Диаграмма с областями'
                ]
                plot_choice = st.selectbox('Тип графика', plot_types)
            
            # Создание графиков зарплаты
            if choice == 'Средняя заработная плата' and 'В среднем за год' in filtered_salary_df.columns:
                fig_salary = create_enhanced_plot(
                    filtered_salary_df, 'Год', ['В среднем за год'],
                    plot_choice, 'Динамика средней заработной платы'
                )
                st.plotly_chart(fig_salary, use_container_width=True)
            
            elif choice == 'Заработная плата по кварталам':
                quarters = ['I', 'II', 'III', 'IV']
                available_quarters = [q for q in quarters if q in filtered_salary_df.columns]
                
                if available_quarters:
                    selected_quarters = st.multiselect(
                        'Выберите кварталы', available_quarters, default=available_quarters
                    )
                    
                    if selected_quarters:
                        fig_quarters = create_enhanced_plot(
                            filtered_salary_df, 'Год', selected_quarters,
                            plot_choice, 'Заработная плата по кварталам'
                        )
                        st.plotly_chart(fig_quarters, use_container_width=True)
            
            elif choice == 'Заработная плата по месяцам':
                months = [
                    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
                ]
                available_months = [m for m in months if m in filtered_salary_df.columns]
                
                if available_months:
                    selected_months = st.multiselect(
                        'Выберите месяцы', available_months, 
                        default=available_months[:6]
                    )
                    
                    if selected_months:
                        fig_months = create_enhanced_plot(
                            filtered_salary_df, 'Год', selected_months,
                            plot_choice, 'Заработная плата по месяцам'
                        )
                        st.plotly_chart(fig_months, use_container_width=True)
    
    # Футер
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; padding: 1rem;'>
        <p>📊 Приложение для анализа статистических данных России</p>
        <p><small>Данные взяты по 2022г. • Версия 2.0</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
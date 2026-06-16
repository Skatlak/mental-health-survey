import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import json

if not firebase_admin._apps:
    try:
        key_json = st.secrets["FIREBASE_KEY"]
        cred_dict = json.loads(key_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except Exception:
        key_path = os.getenv("FIREBASE_KEY", "serviceAccountKey.json")
        if os.path.exists(key_path):
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        else:
            st.error("Ошибка: файл serviceAccountKey.json не найден, и секреты не настроены.")
            st.stop()

db = firestore.client()

st.set_page_config(page_title="Опрос: Ментальное здоровье в ВУЗе", layout="wide")
st.title("Отношение к ментальному здоровью в ВУЗе")
st.markdown("""
Данный опрос направлен на изучение доступности психологической помощи, 
уровня стигмы и востребованных инициатив в университетской среде. 
Ответы анонимны и используются только в учебных целях.
""")

with st.form("mental_health_survey"):
    st.subheader("Блок 1. Общая информация")
    col1, col2 = st.columns(2)
    with col1:
        q1_age = st.number_input("1. Ваш возраст (полных лет)", min_value=14, max_value=60, step=1, value=18)
        q2_gender = st.radio("2. Ваш пол", ["Мужской", "Женский", "Предпочитаю не указывать"])
        q3_year = st.selectbox("3. Ваш курс обучения",
                               ["1 курс", "2 курс", "3 курс", "4 курс", "Магистратура", "Аспирантура"])
    with col2:
        q4_format = st.radio("4. Форма обучения", ["Очная", "Очно-заочная", "Заочная"])
        q5_faculty = st.text_input("5. Ваше направление подготовки")

    st.markdown("---")

    st.subheader("Блок 2. Доступность психологической помощи")
    col1, col2 = st.columns(2)
    with col1:
        q6_know = st.radio("6. Знаете ли вы о наличии психолога в вашем ВУЗе?",
                           ["Да", "Нет", "Слышал(а), но не уверен(а)"])
        q7_info = st.slider(
            "7. Насколько легко найти информацию о психологической помощи в ВУЗе? (1 - очень сложно, 10 - очень легко)",
            1, 10, 5)
        q8_used = st.radio("8. Пользовались ли вы услугами психолога ВУЗа?", ["Да", "Нет", "Планирую обратиться"])
        q9_reasons = st.multiselect("9. Если нет, то почему? (можно несколько)",
                                    ["Не знал(а) о такой услуге", "Не вижу необходимости", "Боюсь осуждения",
                                     "Нет времени", "Не доверяю", "Другое"])
        q10_time = st.radio("10. Сколько времени, по вашему мнению, занимает запись к психологу?",
                            ["Меньше дня", "1-3 дня", "Неделю", "Больше недели", "Не знаю"])
    with col2:
        q11_location = st.radio("11. Удобно ли расположение кабинета психолога?",
                                ["Да", "Нет", "Не знаю, где он находится"])
        q12_schedule = st.radio("12. Устраивает ли вас график работы психолога?", ["Да", "Нет", "Не знаю"])
        q13_trust = st.slider(
            "13. Насколько вы доверяете штатному психологу ВУЗа? (1 - не доверяю, 10 - полностью доверяю)", 1, 10, 5)
        q14_online = st.radio("14. Хотели бы вы иметь возможность онлайн-консультации с психологом?",
                              ["Да", "Нет", "Мне всё равно"])
        q15_pay = st.radio("15. Готовы ли вы платить за психологическую помощь, если она качественная?",
                           ["Да", "Нет", "Только если недорого"])

    st.markdown("---")

    st.subheader("Блок 3. Отношение общества")
    col1, col2 = st.columns(2)
    with col1:
        q16_stigma = st.radio(
            "16. Сталкивались ли вы с неодоброением от общестав при обращении за психологической помощью?",
            ["Да, часто", "Да, иногда", "Нет, никогда", "Не обращался(ась)"])
        q17_source = st.multiselect("17. От кого чаще всего исходит неодоброение? (можно несколько)",
                                    ["От одногруппников", "От преподавателей", "От родителей", "От друзей",
                                     "От общества в целом", "Не сталкивался(ась)"])
        q18_weakness = st.radio("18. Считаете ли вы, что обращение к психологу — это признак слабости?",
                                ["Да", "Нет", "Затрудняюсь ответить"])
        q19_friends = st.radio("19. Обсуждали ли вы свои психологические проблемы с друзьями?",
                               ["Да, часто", "Да, иногда", "Нет, никогда"])
        q20_teachers = st.radio("20. Обсуждали ли вы это с преподавателями?", ["Да", "Нет", "Не было необходимости"])
    with col2:
        q21_fear = st.slider(
            "21. Насколько вы боялись осуждения при мысли об обращении за помощью? (1 - не боялся, 10 - очень боялся)",
            1, 10, 5)
        q22_taboo = st.radio("22. Считаете ли вы тему ментального здоровья табуированной в вашем ВУЗе?",
                             ["Да", "Нет", "Частично"])
        q23_discrim = st.radio("23. Замечали ли вы случаи дискриминации студентов с психологическими проблемами?",
                               ["Да", "Нет", "Не уверен(а)"])
        q24_improve = st.radio("24. Как вы считаете, улучшается ли отношение к ментальному здоровью в обществе?",
                               ["Да", "Нет", "Остаётся прежним"])
        q25_open = st.radio("25. Готовы ли вы открыто говорить о своих психологических трудностях?",
                            ["Да", "Нет", "Только с близкими"])

    st.markdown("---")

    st.subheader("Блок 4. Личный опыт и самочувствие")
    col1, col2 = st.columns(2)
    with col1:
        q26_stress = st.radio("26. Как часто вы испытываете стресс в учёбе?",
                              ["Постоянно", "Часто", "Иногда", "Редко", "Никогда"])
        q27_anxiety = st.radio("27. Как часто вы испытываете тревожность?",
                               ["Постоянно", "Часто", "Иногда", "Редко", "Никогда"])
        q28_sleep = st.slider("28. Как вы оцениваете качество своего сна? (1 - очень плохое, 10 - отличное)", 1, 10, 5)
        q29_burnout = st.radio("29. Испытывали ли вы симптомы академического выгорания?", ["Да", "Нет", "Не уверен(а)"])
        q30_symptoms = st.multiselect("30. Какие симптомы выгорания вы замечали? (можно несколько)",
                                      ["Усталость", "Потеря мотивации", "Раздражительность", "Проблемы со сном",
                                       "Снижение успеваемости", "Апатия", "Не замечал(а)"])
    with col2:
        q31_coping = st.multiselect("31. Как вы обычно справляетесь со стрессом? (можно несколько)",
                                    ["Спорт", "Общение с друзьями", "Хобби", "Сон", "Еда", "Соцсети",
                                     "Ничего не помогает"])
        q32_rest = st.number_input("32. Сколько часов в день вы уделяете отдыху?", min_value=0, max_value=24, step=1,
                                   value=4)
        q33_sport = st.radio("33. Занимаетесь ли вы спортом или физической активностью?",
                             ["Регулярно", "Иногда", "Редко", "Никогда"])
        q34_lonely = st.radio("34. Как часто вы чувствуете одиночество?",
                              ["Постоянно", "Часто", "Иногда", "Редко", "Никогда"])
        q35_state = st.slider("35. Оцените своё текущее психологическое состояние (1 - очень плохое, 10 - отличное)", 1,
                              10, 5)

    st.markdown("---")

    st.subheader("Блок 5. Инициативы и предложения")
    col1, col2 = st.columns(2)
    with col1:
        q36_initiatives = st.multiselect(
            "36. Какие инициативы по поддержке ментального здоровья вам нужны? (можно несколько)",
            ["Бесплатные консультации психолога", "Анонимные чаты поддержки", "Воркшопы по стресс-менеджменту",
             "Комнаты психологической разгрузки", "Гибкий график при выгорании", "Лекции о ментальном здоровье"])
        q37_room = st.radio("37. Хотели бы вы иметь комнату психологической разгрузки в ВУЗе?",
                            ["Да", "Нет", "Мне всё равно"])
        q38_workshop = st.radio("38. Интересуют ли вас воркшопы по управлению стрессом?",
                                ["Да, очень", "Скорее да", "Скорее нет", "Нет"])
        q39_chat = st.radio("39. Хотели бы вы анонимный чат психологической поддержки?", ["Да", "Нет", "Не уверен(а)"])
        q40_lectures = st.radio("40. Нужны ли вам регулярные лекции о ментальном здоровье?", ["Да", "Нет", "Иногда"])
    with col2:
        q41_flexible = st.radio("41. Хотели бы вы гибкий график сдачи заданий при выгорании?",
                                ["Да", "Нет", "Затрудняюсь ответить"])
        q42_formats = st.multiselect("42. Какие форматы поддержки вам наиболее удобны? (можно несколько)",
                                     ["Очные консультации", "Онлайн-консультации", "Групповые занятия",
                                      "Самостоятельные материалы", "Мобильное приложение"])
        q43_volunteer = st.radio("43. Готовы ли вы участвовать в волонтёрских программах поддержки студентов?",
                                 ["Да", "Нет", "Возможно"])
        q44_frequency = st.radio("44. Как часто вы хотели бы получать информацию о ментальном здоровье?",
                                 ["Еженедельно", "Раз в месяц", "Раз в семестр", "Только по необходимости"])
        q45_suggestions = st.text_area("45. Ваши предложения по улучшению ситуации с ментальным здоровьем в ВУЗе")

    st.markdown("---")

    st.subheader("Блок 6. Информированность и образование")
    col1, col2 = st.columns(2)
    with col1:
        q46_sources = st.multiselect("46. Откуда вы получаете информацию о ментальном здоровье? (можно несколько)",
                                     ["Соцсети", "Друзья", "Преподаватели", "Психолог ВУЗа", "Интернет-статьи", "Книги",
                                      "Специалисты"])
        q47_trust_info = st.slider(
            "47. Насколько вы доверяете этой информации? (1 - не доверяю, 10 - полностью доверяю)", 1, 10, 5)
        q48_want_know = st.radio("48. Хотели бы вы больше знать о ментальном здоровье?",
                                 ["Да", "Нет", "Мне достаточно"])
    with col2:
        q49_topics = st.multiselect("49. Какие темы вас интересуют больше всего? (можно несколько)",
                                    ["Стресс-менеджмент", "Тревожность", "Выгорание", "Отношения", "Самооценка", "Сон",
                                     "Тайм-менеджмент"])
        q50_awareness = st.slider(
            "50. Оцените общую осведомлённость студентов вашего ВУЗа о ментальном здоровье (1 - очень низкая, 10 - очень высокая)",
            1, 10, 5)

    st.markdown("---")
    submit = st.form_submit_button("Отправить ответы")

if submit:
    record = {
        "age": int(q1_age),
        "gender": q2_gender,
        "study_year": q3_year,
        "study_format": q4_format,
        "faculty": q5_faculty,
        "know_psychologist": q6_know,
        "info_accessibility": int(q7_info),
        "used_services": q8_used,
        "reasons_no_use": q9_reasons,
        "appointment_time": q10_time,
        "location_convenience": q11_location,
        "schedule_convenience": q12_schedule,
        "trust_level": int(q13_trust),
        "online_preference": q14_online,
        "willing_to_pay": q15_pay,
        "stigma_experience": q16_stigma,
        "stigma_source": q17_source,
        "weakness_perception": q18_weakness,
        "discuss_friends": q19_friends,
        "discuss_teachers": q20_teachers,
        "fear_judgment": int(q21_fear),
        "taboo_topic": q22_taboo,
        "discrimination_observed": q23_discrim,
        "society_improvement": q24_improve,
        "openness": q25_open,
        "stress_frequency": q26_stress,
        "anxiety_frequency": q27_anxiety,
        "sleep_quality": int(q28_sleep),
        "burnout_experience": q29_burnout,
        "burnout_symptoms": q30_symptoms,
        "coping_strategies": q31_coping,
        "rest_hours": int(q32_rest),
        "sport_activity": q33_sport,
        "loneliness_frequency": q34_lonely,
        "current_state": int(q35_state),
        "needed_initiatives": q36_initiatives,
        "relaxation_room": q37_room,
        "workshop_interest": q38_workshop,
        "anonymous_chat": q39_chat,
        "lectures_need": q40_lectures,
        "flexible_schedule": q41_flexible,
        "preferred_formats": q42_formats,
        "volunteer_readiness": q43_volunteer,
        "info_frequency": q44_frequency,
        "suggestions": q45_suggestions,
        "info_sources": q46_sources,
        "info_trust": int(q47_trust_info),
        "want_know_more": q48_want_know,
        "interesting_topics": q49_topics,
        "general_awareness": int(q50_awareness),
        "timestamp": datetime.utcnow()
    }
    try:
        db.collection("mental_health_responses_50q").add(record)
        st.success("Спасибо! Ваш ответ успешно и анонимно сохранен.")
    except Exception as e:
        st.error(f"Ошибка при сохранении: {e}")

st.markdown("---")
if st.checkbox("Показать панель аналитики"):
    docs = db.collection("mental_health_responses_50q").stream()
    data = [doc.to_dict() for doc in docs]

    if not data:
        st.info("Пока нет ни одного ответа. Заполните форму выше, чтобы увидеть данные здесь.")
    else:
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        st.subheader("Последние ответы (сырые данные)")
        st.dataframe(df.head(10), use_container_width=True)

        st.subheader("Визуализация ключевых результатов")

        col_a, col_b = st.columns(2)
        with col_a:
            fig_access = px.histogram(
                df, x="info_accessibility",
                title="Распределение: Доступность информации о помощи (1-10)",
                nbins=10,
                color_discrete_sequence=["#636EFA"]
            )
            st.plotly_chart(fig_access, use_container_width=True)

        with col_b:
            fig_stigma = px.pie(
                df, names="stigma_experience",
                title="Доля ответов: Сталкивались ли со стигмой?"
            )
            st.plotly_chart(fig_stigma, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig_state = px.histogram(
                df, x="current_state",
                title="Распределение: Текущее психологическое состояние (1-10)",
                nbins=10,
                color_discrete_sequence=["#EF553B"]
            )
            st.plotly_chart(fig_state, use_container_width=True)

        with col_d:
            fig_burnout = px.pie(
                df, names="burnout_experience",
                title="Доля ответов: Испытывали ли выгорание?"
            )
            st.plotly_chart(fig_burnout, use_container_width=True)

        st.subheader("Популярность инициатив по поддержке")
        all_initiatives = [item for sublist in df["needed_initiatives"].dropna() for item in sublist]
        init_df = pd.DataFrame(all_initiatives, columns=["Инициатива"])
        fig_init = px.bar(
            init_df["Инициатива"].value_counts().reset_index(),
            x="count", y="Инициатива", orientation="h",
            title="Количество упоминаний инициатив",
            labels={"count": "Количество выборов", "Инициатива": "Вариант ответа"},
            color="count",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_init, use_container_width=True)

        st.subheader("Источники информации о ментальном здоровье")
        all_sources = [item for sublist in df["info_sources"].dropna() for item in sublist]
        sources_df = pd.DataFrame(all_sources, columns=["Источник"])
        fig_sources = px.bar(
            sources_df["Источник"].value_counts().reset_index(),
            x="count", y="Источник", orientation="h",
            title="Популярность источников информации",
            labels={"count": "Количество упоминаний", "Источник": "Источник"},
            color="count",
            color_continuous_scale="Greens"
        )
        st.plotly_chart(fig_sources, use_container_width=True)

        st.subheader("Частота стресса и тревожности")
        col_e, col_f = st.columns(2)
        with col_e:
            fig_stress = px.histogram(
                df, x="stress_frequency",
                title="Распределение: Частота стресса в учёбе",
                category_orders={"stress_frequency": ["Никогда", "Редко", "Иногда", "Часто", "Постоянно"]},
                color_discrete_sequence=["#FFA15A"]
            )
            st.plotly_chart(fig_stress, use_container_width=True)

        with col_f:
            fig_anxiety = px.histogram(
                df, x="anxiety_frequency",
                title="Распределение: Частота тревожности",
                category_orders={"anxiety_frequency": ["Никогда", "Редко", "Иногда", "Часто", "Постоянно"]},
                color_discrete_sequence=["#AB63FA"]
            )
            st.plotly_chart(fig_anxiety, use_container_width=True)
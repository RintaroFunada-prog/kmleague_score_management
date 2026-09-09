import streamlit as st
import pandas as pd
import os
import time
import plotly.express as px
from datetime import date

from datetime import date

st.set_page_config(
    page_title="KMリーグ『金融麻雀リーグ』",
    page_icon="🀄",
    layout="wide"
)

PLAYER_FILE = "players.csv"
RESULT_FILE = "results.csv"

# =====================================
# マスタ読込
# =====================================

players_df = pd.read_csv(
    PLAYER_FILE,
    encoding="utf-8-sig"
)

if not os.path.exists(RESULT_FILE):
    pd.DataFrame(
        columns=[
            "大会",
            "対局日",
            "氏名",
            "順位",
            "ポイント"
        ]
    ).to_csv(
        RESULT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

results_df = pd.read_csv(
    RESULT_FILE,
    encoding="utf-8-sig"
)

player_list = players_df["氏名"].tolist()

# =====================================
# 画面
# =====================================

st.title("🀄 KMリーグ『金融麻雀リーグ』")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "参加者・個人ランキング",
        "対局結果入力",
        "チームランキング",
        "対局一覧"
    ]
)

# =====================================
# 参加者・個人ランキング
# =====================================

with tab1:

    st.subheader("参加者・個人ランキング")

    ranking_df = players_df.copy()

    if not results_df.empty:

        personal_rank = (
            results_df
            .groupby("氏名")
            .agg(
                累計ポイント=("ポイント", "sum"),
                対局数=("順位", "count")
            )
            .reset_index()
        )

        ranking_df = pd.merge(
            ranking_df,
            personal_rank,
            on="氏名",
            how="left"
        )

    else:

        ranking_df["累計ポイント"] = 0
        ranking_df["対局数"] = 0

    ranking_df["累計ポイント"] = (
        ranking_df["累計ポイント"]
        .fillna(0)
        .astype(int)
    )

    ranking_df["対局数"] = (
        ranking_df["対局数"]
        .fillna(0)
        .astype(int)
    )

    # =====================================
    # 個人順位算出
    # =====================================

    ranking_df["個人順位"] = pd.NA

    mask = ranking_df["対局数"] > 0

    ranking_df.loc[mask, "個人順位"] = (
        ranking_df.loc[mask, "累計ポイント"]
        .rank(
            method="min",
            ascending=False
        )
        .astype(int)
    )

    ranking_df = ranking_df.sort_values(
        by="個人順位",
        na_position="last"
    )

    # =====================================
    # TOP3表示
    # =====================================

    top3_df = (
        ranking_df[
            ranking_df["対局数"] > 0
        ]
        .sort_values(
            "累計ポイント",
            ascending=False
        )
        .head(3)
    )

    if not top3_df.empty:

        st.markdown("## 🏆 TOP3")

        col1, col2, col3 = st.columns(3)

        columns = [col1, col2, col3]
        medals = ["🥇", "🥈", "🥉"]

        for i, (_, row) in enumerate(top3_df.iterrows()):

            with columns[i]:
                st.metric(
                    label=f"{medals[i]} {row['氏名']}",
                    value=f"{row['累計ポイント']} pt",
                    delta=f"{row['対局数']} 半荘"
)

        st.divider()

    # =====================================
    # 一覧表示
    # =====================================

    display_df = ranking_df[
        [
            "氏名",
            "チーム",
            "個人順位",
            "累計ポイント",
            "対局数"
        ]
    ].copy()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
# =====================================
# 対局結果入力
# =====================================

with tab2:

    st.subheader("対局結果入力")
    st.info("""
    【☆注意事項☆】

    ・1卓ごとに代表者1名が結果を登録してください。（同一対局の重複登録は禁止）

    ・誤入力（スコア、対局者など）があった場合、スコア用紙へ誤入力内容を記載し、運営までご提出ください。
    ※アプリ上での修正・削除機能はありません。

    ・登録後も入力内容が画面上に残る場合があります。その際はブラウザを再読み込みしてください。
    """)
    if len(player_list) < 4:
        st.warning(
            "players.csvに4名以上登録してください。"
        )
    else:
        with st.form("result_form"):
            ##要修正
            tournament = (
                # "テスト"
                "第3回大会"
            )

            game_date = st.date_input(
                "対局日",
                date.today()
            )

            st.markdown("### 順位入力")

            select_players = ["選択してください"] + player_list
            # =====================
            # 1位
            # =====================

            st.markdown("### 🥇 1位")

            p1 = st.selectbox(
                "氏名",
                select_players,
                key="p1"
            )

            score1 = st.number_input(
                "ポイント",
                value=45,
                key="score1"
            )

            # =====================
            # 2位
            # =====================

            st.markdown("### 🥈 2位")

            p2 = st.selectbox(
                "氏名",
                select_players,
                key="p2"
            )

            score2 = st.number_input(
                "ポイント",
                value=10,
                key="score2"
            )

            # =====================
            # 3位
            # =====================

            st.markdown("### 🥉 3位")

            p3 = st.selectbox(
                "氏名",
                select_players,
                key="p3"
            )

            score3 = st.number_input(
                "ポイント",
                value=-10,
                key="score3"
            )

            # =====================
            # 4位
            # =====================

            st.markdown("### 🏅 4位")

            p4 = st.selectbox(
                "氏名",
                select_players,
                key="p4"
            )

            score4 = st.number_input(
                "ポイント",
                value=-45,
                key="score4"
            )
            st.divider()

            submit = st.form_submit_button(
                "結果登録",
                use_container_width=True
            )

            if submit:

                players = [p1, p2, p3, p4]

                score_sum = (
                    score1 +
                    score2 +
                    score3 +
                    score4
                )

                if "選択してください" in players:

                    st.error(
                        "全員の参加者を選択してください。"
                    )

                elif len(set(players)) != 4:

                    st.error(
                        "同じ参加者を重複して選択できません。"
                    )

                elif score_sum != 0:

                    st.error(
                        f"ポイント合計が0ではありません（現在:{score_sum}）"
                    )

                elif not (score1 >= score2 >= score3 >= score4):
                    st.error(
                        "順位に対するポイントの大小関係が不正です。（1位 ≥ 2位 ≥ 3位 ≥ 4位 となるよう入力してください）"
                    )

                else:
                    from datetime import datetime
                    table_id = datetime.now().strftime(
                        "T%Y%m%d%H%M%S"
                    )
                    new_result = pd.DataFrame({

                        "大会": [
                            tournament,
                            tournament,
                            tournament,
                            tournament
                        ],

                        "卓": [
                            table_id,
                            table_id,
                            table_id,
                            table_id
                        ],

                        "対局日": [
                            game_date,
                            game_date,
                            game_date,
                            game_date
                        ],

                        "氏名": [
                            p1,
                            p2,
                            p3,
                            p4
                        ],

                        "順位": [
                            1,
                            2,
                            3,
                            4
                        ],

                        "ポイント": [
                            score1,
                            score2,
                            score3,
                            score4
                        ]
                    })

                    results_df = pd.concat(
                        [results_df, new_result],
                        ignore_index=True
                    )

                    results_df.to_csv(
                        RESULT_FILE,
                        index=False,
                        encoding="utf-8-sig"
                    )

                    st.success(
                        "結果を保存しました。"
                    )

                    time.sleep(2.5)

                    st.rerun()

# =====================================
# チームランキング
# =====================================

with tab3 :

    st.subheader("チームランキング")

    if results_df.empty:

        st.info(
            "まだ対局結果が登録されていません。"
        )

    else:

        merge_df = pd.merge(
            results_df,
            players_df,
            on="氏名",
            how="left"
        )

        team_rank = (
            merge_df
            .groupby("チーム")
            .agg(
                総ポイント=("ポイント", "sum"),
                対局数=("氏名", "count")
            )
            .reset_index()
            .sort_values(
                "総ポイント",
                ascending=False
            )
        )
        # =====================================
        # TOP3チーム表示
        # =====================================

        top3_team_df = (
            team_rank
            .sort_values(
                "総ポイント",
                ascending=False
            )
            .head(3)
        )

        if not top3_team_df.empty:

            st.markdown("## 🏆 チームTOP3")

            col1, col2, col3 = st.columns(3)

            columns = [col1, col2, col3]
            medals = ["🥇", "🥈", "🥉"]

            for i, (_, row) in enumerate(top3_team_df.iterrows()):

                with columns[i]:

                    st.metric(
                        label=f"{medals[i]} {row['チーム']}",
                        value=f"{row['総ポイント']} pt",
                        delta=f"{row['対局数']} 半荘"

                    )

            st.divider()

        st.dataframe(
            team_rank,
            use_container_width=True
        )

        fig = px.bar(
            team_rank,
            x="チーム",
            y="総ポイント",
            text="総ポイント"
        )

        fig.update_layout(
            xaxis_title="チーム",
            yaxis_title="総ポイント"
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
# =====================================
# 対局一覧
# =====================================

with tab4:

    st.subheader("対局一覧")

    if results_df.empty:

        st.info(
            "まだ対局結果が登録されていません。"
        )

    else:

        # 日付順
        results_view = results_df.copy()

        results_view["対局日"] = pd.to_datetime(
            results_view["対局日"]
        )

        game_dates = (
            results_view["対局日"]
            .sort_values(ascending=False)
            .dt.date
            .unique()
        )

        for game_date in game_dates:

            st.markdown(
                f"## 📅 {game_date}"
            )

            date_df = results_view[
                results_view["対局日"].dt.date
                == game_date
            ]

            table_ids = (
                date_df["卓"]
                .dropna()
                .unique()
            )

            for table_id in table_ids:

                game_df = (
                    date_df[
                        date_df["卓"] == table_id
                    ]
                    .sort_values("順位")
                )
                display_df = game_df[
                    [
                        "順位",
                        "氏名",
                        "ポイント"
                    ]
                ].copy()

                display_df["順位"] = display_df["順位"].replace({
                    1: "🥇",
                    2: "🥈",
                    3: "🥉",
                    4: "4️⃣"
                })

                st.markdown(
                    f"### 卓ID : {table_id}"
                )

                st.dataframe(
                    display_df,
                    hide_index=True,
                    use_container_width=True
                )
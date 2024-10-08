import pandas as pd
import numpy as np
import streamlit as st
import xlrd

# 테스트 데이터 로드
df = pd.read_excel("./data/testdata_20241008.xlsx", engine="openpyxl", usecols="A:K", sheet_name=1)


# 페이지 꾸미기
if __name__ == "__main__" :
    st.set_page_config(layout = "wide")
    st.title("해외주식 양도세 줄이기 테스트")
    accounting_select_box = st.selectbox("계좌번호", (list(df['계좌번호'].unique())))
    st.write(f"고객명 : {df[df['계좌번호']==accounting_select_box]['고객명'].unique()[0]}")
    rate = st.number_input("환율을 입력하세요", value=1376.3)

    df_rcmd = df[(df['계좌번호']==accounting_select_box) & (df['추천 여부']=="Y")].reset_index(drop=True)

    col1, col2 = st.columns(2)
    with col1 :
        container1 = st.container(border=True)
        container1.write(df_rcmd)
        row1 = st.columns(3)
        row2 = st.columns(3)
        unique_value = 0
        sum_loss_amount = 0
        sum_sell_amount = 0

        for ind, col in enumerate(row1+row2):
            unique_value += 1
            tile = col.container(height=200)
            tile.write(df_rcmd.loc[ind]['상품명'])
            tile.write(f"보유수량 : {df_rcmd.loc[ind]['보유수량']}")

            if 'quantities' not in st.session_state:
                st.session_state.quantities = list(df_rcmd['추천매도수량'])
            if 'prices' not in st.session_state:
                st.session_state.prices = list(df_rcmd['추천매도단가(전일종가, 외화)'])


            with tile :
                if st.button("수량 -", key=f"NB_minus{unique_value}"):
                    st.session_state.quantities[ind] -= 1
                if st.button("수량 +", key=f"NB_plus{unique_value}") :
                    st.session_state.quantities[ind] += 1
                st.write("추천매도수량 : ", st.session_state.quantities[ind])

                if st.button("가격 -", key=f"PR_minus{unique_value}"):
                    if st.session_state.prices[ind] >= 1 :
                        if (len(str(df_rcmd.loc[ind]['추천매도단가(전일종가, 외화)']).split(".")[1]) == 4) and st.session_state.prices[ind] ==1 :
                            st.session_state.prices[ind] -= 0.0001
                        else:
                            st.session_state.prices[ind] -= 0.01
                    else :
                        st.session_state.prices[ind] -= 0.0001
                if st.button("가격 +", key=f"PR_plus{unique_value}") :
                    if st.session_state.prices[ind] >= 1:
                        st.session_state.prices[ind] += 0.01
                    else:
                        st.session_state.prices[ind] += 0.0001

                price1 = round(st.session_state.prices[ind], 3)
                price2 = round(st.session_state.prices[ind], 5)

                st.write("추천매도단가 : ", price1 if st.session_state.prices[ind] >=1 else price2)

                st.write(f"종목당 손실액 :  {int(np.ceil(st.session_state.prices[ind]*rate*st.session_state.quantities[ind] - df_rcmd.loc[ind]['비용포함원화매입단가']*st.session_state.quantities[ind])):,}")
                st.write(f"종목당 매도금액 : {int(np.floor(st.session_state.prices[ind]*rate*st.session_state.quantities[ind])):,}")
            sum_loss_amount += np.ceil(st.session_state.prices[ind]*rate*st.session_state.quantities[ind] - df_rcmd.loc[ind]['비용포함원화매입단가']*st.session_state.quantities[ind])
            sum_sell_amount += np.floor(st.session_state.prices[ind]*rate*st.session_state.quantities[ind])

    with col2 :
        container2 = st.container(border=True)
        with container2 :
            st.write(f"손실중인 금액 : {int(sum_loss_amount):,}")
            st.write(f"매도중인 금액 : {int(sum_sell_amount):,}")
            st.write(f"예상절세 금액 : {int(min(df_rcmd.loc[0]['양도소득세'], np.floor(-sum_loss_amount*0.22))):,}")
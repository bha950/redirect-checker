import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st

# Title
st.title("🔗 Redirect Checker Tool")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV (must contain 'url' column)", type=["csv"])

# Redirect Checker Function
def check_redirect(url):
    try:
        if not str(url).startswith("http"):
            url = "http://" + str(url)

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=15)

        redirect_chain = " -> ".join([resp.url for resp in response.history])

        return {
            "Original URL": url,
            "Final URL": response.url,
            "Status Code": response.status_code,
            "Redirect Chain": redirect_chain if redirect_chain else "No Redirect"
        }

    except Exception as e:
        return {
            "Original URL": url,
            "Final URL": "Error",
            "Status Code": "Error",
            "Redirect Chain": str(e)
        }

# Run app
if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='latin1')

    if 'url' not in df.columns:
        st.error("CSV must contain 'url' column")
    else:
        if st.button("Start Checking"):
            results = []
            max_threads = 20

            st.info("Processing URLs...")

            progress_bar = st.progress(0)

            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                futures = [executor.submit(check_redirect, url) for url in df['url']]

                for i, future in enumerate(as_completed(futures)):
                    results.append(future.result())
                    progress_bar.progress((i + 1) / len(futures))

            result_df = pd.DataFrame(results)

            st.success("Processing Completed ✅")
            st.dataframe(result_df)

            # Download button
            csv = result_df.to_csv(index=False).encode('utf-8')

            st.download_button(
                label="📥 Download Results",
                data=csv,
                file_name="redirect_output.csv",
                mime="text/csv"
            )
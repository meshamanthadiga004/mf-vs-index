import pandas as pd, requests

codes = {
    "Nifty50 Index (UTI)":     120716,
    "SBI Large Cap":           119598,
    "ICICI Pru Large Cap":     120586,
    "HDFC Large Cap":          119018,
    "Mirae Large Cap":         118825,
    "Axis Large Cap":          120465,
    "Nippon Large Cap":        118632,
    "Kotak Large Cap":         120152,
    "Canara Robeco Large Cap": 118269,
}

frames = []
for name, code in codes.items():
    print("Downloading", name)
    d = requests.get(f"https://api.mfapi.in/mf/{code}").json()["data"]
    s = pd.DataFrame(d).assign(date=lambda x: pd.to_datetime(x.date, dayfirst=True),
                               nav=lambda x: x.nav.astype(float))
    frames.append(s.set_index("date")["nav"].rename(name))

navs = pd.concat(frames, axis=1, sort=True).sort_index().loc["2020-10-01":"2026-10-13"].dropna()  # fixed window = reproducible
navs.to_csv("../data/navs.csv")
print("Done:", navs.shape[0], "rows x", navs.shape[1], "funds")

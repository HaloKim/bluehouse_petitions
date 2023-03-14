import pandas as pd
import requests
from lxml.html import fromstring
from tqdm import tqdm
import gc
import ray
ray.init()


@ray.remote
def main(data, h, ram, iteration):
    if ram == 0 & h > iteration: # 처음위치
        s = h
        e = s-iteration
    elif 0 <= h-iteration*ram <= iteration: # 마지막 위치
        s = h-iteration*ram
        e = -1
    elif h-iteration*ram < 0: # 이전에 마지막 위치를 도달 했으면 빈 df 리턴
        return data.append(pd.Series([None for _ in range(len(columns))]), ignore_index=True)
    else:
        s = h-iteration*ram
        e = s-iteration
    for code in tqdm(range(s, e, -1)):
        try:
            url = "http://webarchives.pa.go.kr/19th/www.president.go.kr/petitions/{}".format(code)
            res = requests.get(url)
            parser = fromstring(res.text)

            title = parser.xpath("/html/body/div[3]/div[2]/section[2]/div[2]/div[1]/div[2]/div[1]/div/h3/text()")
            status = parser.xpath(
                "/html/body/div[3]/div[2]/section[2]/div[2]/div[1]/div[2]/div[1]/div/div[1]/h4/text()")
            personnel = parser.xpath(
                "/html/body/div[3]/div[2]/section[2]/div[2]/div[1]/div[2]/div[1]/div/h2/span/text()")
            category = parser.xpath(
                "/html/body/div[3]/div[2]/section[2]/div[2]/div[1]/div[2]/div[1]/div/div[2]/ul/li[1]/text()")
            start = parser.xpath(
                "/html/body/div[3]/div[2]/section[2]/div[2]/div[1]/div[2]/div[1]/div/div[2]/ul/li[2]/text()")
            end = parser.xpath(
                "/html/body/div[3]/div[2]/section[2]/div[2]/div[1]/div[2]/div[1]/div/div[2]/ul/li[3]/text()")
            q = parser.xpath("/html/body/div[3]/div[2]/section[2]/div[2]/div[1]/div[2]/div[1]/div/div[4]/div[2]/text()")
            a = parser.xpath("/html/body/div[3]/div[2]/section[2]/div[2]/div[1]/div[2]/div[1]/div/div[5]/div/text()")
            data = data.append(pd.Series([code, *title, ' '.join(status), *personnel, *category, *start, *end,
                                          ' '.join(q),
                                          ' '.join(a)]), ignore_index=True)
        except:
            if len(data) > 2:
                return data
            else:
                return data.append(pd.Series([None for _ in range(len(columns))]), ignore_index=True)
    return data


worker = 16
size = 3000
total = round(605368/(size*worker))
columns = ['number', '제목', '답변상태', '참여인원', '카테고리', '청원시작', '청원마감', '청원내용', '답변원고']
for i in range(total):
    df = pd.DataFrame()
    df = ray.put(df)
    starting = 605368 - (size*worker*i)
    ans = [main.remote(data=df, h=starting, ram=n, iteration=size) for n in range(worker)]
    ans = ray.get(ans)
    ans = pd.concat(ans, ignore_index=True)

    ans.columns = columns
    ans = ans.dropna(subset=['청원시작']).reset_index(drop=True)

    ans.to_parquet(f'Bluehouse{i}.parquet', engine='pyarrow', compression='gzip', index=False)
    print(f"{i}th FIN")
    del df
    del ans
    gc.collect()
ray.shutdown()

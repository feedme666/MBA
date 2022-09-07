from django.shortcuts import render
from django.http import HttpResponse
from keijiban.forms import KakikomiForm
import requests
import json
import pandas as pd
import xlsxwriter
import io

def kakikomi(request):
    f = KakikomiForm()
    if request.method == 'POST': # POSTの時だけ処理する
        f = KakikomiForm(request.POST) # POSTで送信した値をform変数に格納
        if f.is_valid(): # formの値が正当な時(バリデーションチェックを走らせる)
            y=int(f.data['year'])
            m=int(f.data['month'])
    # 空のデータベース作成
            url_search_jour = '%28%22N+Engl+J+Med%22%5BJournal%5D+OR+%22JAMA%22%5BJournal%5D+OR+%22Lancet%22%5BJournal%5D+OR+%22Ann+Intern+Med%22%5BJournal%5D+OR+%22Crit+Care+Med%22%5BJournal%5D+OR+%22Am+J+Respir+Crit+Care+Med%22%5BJournal%5D+OR+%22Chest%22%5BJournal%5D+OR+%22BMJ%22%5BJournal%5D+OR+%22J+Trauma+Acute+Care+Surg%22%5BJournal%5D+OR+%22Intensive+Care+Med%22%5BJournal%5D+OR+%22Crit+Care%22%5BJournal%5D+OR+%22JAMA+Intern+Med%22%5BJournal%5D+OR+%22Clin%20Infect%20Dis%22%5BJournal%5D+OR+%22Circulation%22%5BJournal%5D+OR+%22Stroke%22%5BJournal%5D%29'
            url_search_base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term='# それぞれの雑誌をpubmed内で検索
            url_something='+AND+%28clinical+trial%5BPT%5D+OR+controlled+clinical+trial%5Bpt%5D+OR+guideline%5Bpt%5D+OR+meta-analysis%5BFpt%5D+OR+randomized+controlled+trial%5BPT%5D+OR+review%5BPT%5D+OR+systematic+review%5BFilter%5D%29&retmax=500&retmode=json&datetype=pdat'
            if m<9:
                    url_search = url_search_base + url_search_jour+ url_something+\
                        '&maxdate='+str(y)+'/0'+str(m+1)+'/01'\
                            '&mindate='+str(y)+'/0'+str(m)+'/01'
            elif m == 9:
                    url_search = url_search_base + url_search_jour+ url_something+\
                        '&maxdate='+str(y)+'/10/01'\
                            '&mindate='+str(y)+'/09/01'
            else:
                    url_search = url_search_base + url_search_jour+ url_something+\
                        '&maxdate='+str(y)+'/'+str(m+1)+'/01'\
                            '&mindate='+str(y)+'/'+str(m)+'/01'

            response = requests.get(url_search)
            response_json = response.json()
            pmids = response_json['esearchresult']['idlist']
            url_summary = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id='
            url_pmid=str()
            for pmid in pmids:
                url_pmid= url_pmid+pmid+','
            url_pmid = url_pmid[:-1]
            res_sum = requests.get(url_summary+url_pmid)
            res_sum_json= res_sum.json()
            df_jour = pd.DataFrame()
            for pmid in pmids:
                series = pd.DataFrame(
                    data={'pmid':[pmid],
                    'fulljournalname':res_sum_json['result'][pmid]['fulljournalname'],
                    'title':res_sum_json['result'][pmid]['title'],
                    'url':['https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/'],
                    })
                df_jour=pd.concat([df_jour, series], axis=0)
            df_jour = df_jour.sort_values('fulljournalname', ascending=True)
    # csvファイルに吐き出し
            output = io.BytesIO()
            writer = pd.ExcelWriter
            filename = str(y)+'_'+str(m)+'mjw.xlsx'
            sheet_name = 'sheet1'
            df_jour.to_excel(output,index=False,sheet_name=sheet_name)
            writer.close
            output.seek(0)
            response = HttpResponse(output, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response

    return render(request, 'keijiban/kakikomiform.html', {'form1': f})
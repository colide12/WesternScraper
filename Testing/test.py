import requests
from bs4 import BeautifulSoup as bs


import urllib, http.cookiejar
cj = http.cookiejar.LWPCookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)) 
urllib.request.install_opener(opener)
 
params = urllib.parse.urlencode({"mode":"login", "pixiv_id":'jjy911018', "pass":'3gkrsus3qks'})
params = params.encode('utf-8')
req = urllib.request.Request("http://www.pixiv.net/index.php", params)
res = opener.open(req)

# LOGIN_INFO = {
#     'si_id': 'jjy911018',
#     'si_pwd': '%3gkrsus3qksM'
#     }

# with requests.Session() as s:
# 	r = s.get('https://lib.snu.ac.kr')
# 	login_req = s.post('https://sso.snu.ac.kr/safeidentity/modules/auth_idpwd', data=LOGIN_INFO)
# 	print(login_req.status_code)


# LOGIN_INFO = {
#     'userId': 'colide',
#     'userPassword': '?3gkrsus3qksC'
# }
# with requests.Session() as s:
#     # 우선 클리앙 홈페이지에 들어가 봅시다.
#     first_page = s.get('https://www.clien.net/service')
#     html = first_page.text
#     soup = bs(html, 'html.parser')
#     csrf = soup.find('input', {'name': '_csrf'}) # input태그 중에서 name이 _csrf인 것을 찾습니다.
#     print(csrf['value']) # 위에서 찾은 태그의 value를 가져옵니다.

#     # 이제 LOGIN_INFO에 csrf값을 넣어줍시다.
#     # (p.s.)Python3에서 두 dict를 합치는 방법은 {**dict1, **dict2} 으로 dict들을 unpacking하는 것입니다.
#     LOGIN_INFO = {**LOGIN_INFO, **{'_csrf': csrf['value']}}
#     print(LOGIN_INFO)

    # 이제 다시 로그인을 해봅시다.
    # login_req = s.post('https://www.clien.net/service/login', data=LOGIN_INFO)
    # # 어떤 결과가 나올까요? (200이면 성공!)
    # print(login_req.status_code)
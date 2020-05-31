# pylint: disable=no-member, unused-variable, eval-used, too-few-public-methods, duplicate-code
"""Class and function for working with VK API"""
import vk
from main.models import VKToken


def vk_api(request, method: str, **kwargs) -> dict:
    """
    Function for making VK API requests

    :param request: HttpRequest object
    :param method: VK API method
    :param kwargs: method's kwargs
    :return: dict with response
    """
    query = VKToken.objects.filter(user__id=request.user.id)
    token = query[0].token if query else ''
    session = vk.API(vk.Session(access_token=token))
    return eval('vk.API(vk.Session(access_token=token)).' + method)(v=5.103, **kwargs)


class VKSearchScripts:
    """VK Scripts for using execute VK API method"""
    by_groups_cities_universities = """
                            var universities = {universities};
                            var cities = {cities};
                            var res = [];
                            var i = 0;

                            while (i < universities.length) {{
                                var t = 0;
                                while (t < cities.length) {{
                                    var users = API.users.search({{
                                                           "q": {q},
                                                           "count": {count},
                                                           "country": {country_id},
                                                           "hometown": cities[t],
                                                           "university": universities[i],
                                                           "sex": {sex},
                                                           "age_from": {age_from},
                                                           "age_to": {age_to},
                                                           "has_photo": {has_photo},
                                                           "group_id": {group_id},
                                                           "fields": "photo_400_orig,domain,relation,sex"      
                                                           }});
                                    res.push(users);
                                    t = t + 1;
                                }}
                                i = i + 1;
                            }}
                            return res;
                    """
    by_cities_universities = """
                        var universities = {universities};
                        var cities = {cities};
                        var res = [];
                        var i = 0;

                        while (i < universities.length) {{
                            var t = 0;
                            while (t < cities.length) {{
                                var users = API.users.search({{
                                                       "q": {q},
                                                       "count": {count},
                                                       "country": {country_id},
                                                       "hometown": cities[t],
                                                       "university": universities[i],
                                                       "sex": {sex},
                                                       "age_from": {age_from},
                                                       "age_to": {age_to},
                                                       "has_photo": {has_photo},
                                                       "fields": "photo_400_orig,domain,relation,sex"      
                                                       }});
                                res.push(users);
                                t = t + 1;
                            }}
                            i = i + 1;
                        }}
                        return res;
                """
    by_cities = """
                                    var cities = {cities};
                                    var res = [];
                                    var i = 0;

                                    while (i < cities.length) {{
                                        var users = API.users.search({{
                                                                "q": {q},
                                                                "count": {count},
                                                                "country": {country_id},
                                                                "hometown": cities[i],
                                                                "sex": {sex},
                                                                "age_from": {age_from},
                                                                "age_to": {age_to},
                                                                "has_photo": {has_photo},
                                                                "fields": "photo_400_orig,domain,relation,sex"      
                                                            }});
                                        res.push(users);
                                        i = i + 1;
                                    }}
                                    return res;
                            """
    by_universities = """
                                    var universities = {universities};
                                    var res = [];
                                    var i = 0;

                                    while (i < universities.length) {{
                                        var users = API.users.search({{
                                                                "q": {q},
                                                                "count": {count},
                                                                "country": {country_id},
                                                                "sex": {sex},
                                                                "university": universities[i],
                                                                "age_from": {age_from},
                                                                "age_to": {age_to},
                                                                "has_photo": {has_photo},
                                                                "fields": "photo_400_orig,domain,relation,sex"      
                                                            }});
                                        res.push(users);
                                        i = i + 1;
                                    }}
                                    return res;
                            """
    by_groups_cities = """
                        var groups = {groups};
                        var cities = {cities};
                        var res = [];
                        var i = 0;

                        while (i < groups.length) {{
                            var t = 0;
                            while (t < cities.length) {{
                                var users = API.users.search({{
                                                       "q": {q},
                                                       "count": {count},
                                                       "country": {country_id},
                                                       "hometown": cities[t],
                                                       "group_id": groups[i],
                                                       "sex": {sex},
                                                       "age_from": {age_from},
                                                       "age_to": {age_to},
                                                       "has_photo": {has_photo},
                                                       "fields": "photo_400_orig,domain,relation,sex"      
                                                       }});
                                res.push(users);
                                t = t + 1;
                            }}
                            i = i + 1;
                        }}
                        return res;
                """
    by_groups_universities = """
                        var groups = {groups};
                        var universities = {universities};
                        var res = [];
                        var i = 0;

                        while (i < groups.length) {{
                            var t = 0;
                            while (t < universities.length) {{
                                var users = API.users.search({{
                                                       "q": {q},
                                                       "count": {count},
                                                       "country": {country_id},
                                                       "university": universities[t],
                                                       "group_id": groups[i],
                                                       "sex": {sex},
                                                       "age_from": {age_from},
                                                       "age_to": {age_to},
                                                       "has_photo": {has_photo},
                                                       "fields": "photo_400_orig,domain,relation,sex"      
                                                       }});
                                res.push(users);
                                t = t + 1;
                            }}
                            i = i + 1;
                        }}
                        return res;
                """
    by_groups = """
                        var groups = {groups};
                        var res = [];
                        var i = 0;

                        while (i < groups.length) {{
                            var users = API.users.search({{
                                                    "q": {q},
                                                    "count": {count},
                                                    "country": {country_id},
                                                    "sex": {sex},
                                                    "age_from": {age_from},
                                                    "age_to": {age_to},
                                                    "has_photo": {has_photo},
                                                    "group_id": groups[i],
                                                    "fields": "photo_400_orig,domain,relation,sex"      
                                                }});
                            res.push(users);
                            i = i + 1;
                        }}
                        return res;
                """
    by_friends = """
                        var friends = {friends};
                        var res = [];
                        var i = 0;

                        while (i < friends.length) {{
                            var users = API.friends.get({{
                                                   "user_id": friends[i],
                                                   "fields": "photo_400_orig,domain,relation,sex"      
                                                   }});
                            res.push(users);
                            i = i + 1;
                        }}
                        return res;
                """

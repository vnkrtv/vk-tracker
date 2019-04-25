from VK_UserInfo import *

class VK_UserAnalizer:

    def __init__(self, domain, date1, date2):

        if not MongoDB().checkDomain(domain):
            raise Exception('No user with input domain in base')

        self._newInf = MongoDB().loadUserInfo(domain=domain, date=date2)
        self._oldInf = MongoDB().loadUserInfo(domain=domain, date=date1)

        print(self._newInf['wall'])
        #self.checkDates(date1, date2);


    def checkDates(self, date1, date2):
        #"{hour:02}-{minutes:02} {day}-{month:02}-{year}".format(**user['date'])
        date1 = tuple(map(int, date1.replace(' ', '-').split('-')))
        date2 = tuple(map(int, date2.replace(' ', '-').split('-')))

        for i in range(4, 1, -1):
            if date1[i] != date2[i]:
                if date2[i] > date1[i]:
                    buff_dict    = self._newInf
                    self._newInf = self._oldInf
                    self._oldInf = buff_dict
                    return

        for i in range(0, 2):
            if date1[i] != date2[i]:
                if date2[i] > date1[i]:
                    buff_dict    = self._newInf
                    self._newInf = self._oldInf
                    self._oldInf = buff_dict
                    return


    def cmpMainInfo(self):
        oldMain = self._oldInf['main_info']
        newMain = self._newInf['main_info']

        cmpDict = {}

        for (old, new) in zip(oldMain, newMain):
            if oldMain[old] != newMain[new]:
                if type(oldMain[old]) is not dict:
                    cmpDict[old] = {
                        'old': oldMain[old],
                        'new': newMain[new]
                    }

        return cmpDict


    def cmpFriends(self):
        oldFriends = self._oldInf['friends']['items']
        newFriends = self._newInf['friends']['items']

        cmpDict = {}

        for friend in oldFriends:
            id = friend['id']
            cmpDict[id] = [friend, 0]

        for friend in newFriends:
            id = friend['id']

            if id in cmpDict:
                cmpDict.pop(id)
            else:
                cmpDict[id] = [friend, 1]

        changeDict = {
            'new': [],
            'deleted': []
        }

        for item in cmpDict:
            if cmpDict[item][1]:
                changeDict['new'].append(cmpDict[item][0])
            else:
                changeDict['deleted'].append(cmpDict[item][0])

        return changeDict


    def cmpFollowers(self):
        oldFollowers = self._oldInf['followers']['items']
        newFollowers = self._newInf['followers']['items']

        cmpDict = {}

        for follower in oldFollowers:
            id = follower['id']
            cmpDict[id] = [follower, 0]

        for follower in newFollowers:
            id = follower['id']

            if id in cmpDict:
                cmpDict.pop(id)
            else:
                cmpDict[id] = [follower, 1]

        changeDict = {
            'new': [],
            'deleted': []
        }

        for item in cmpDict:
            if cmpDict[item][1]:
                changeDict['new'].append(cmpDict[item][0])
            else:
                changeDict['deleted'].append(cmpDict[item][0])

        return changeDict


    def cmpGroups(self):
        oldGroups = self._oldInf['groups']['items']
        newGroups = self._newInf['groups']['items']

        cmpDict = {}

        for group in oldGroups:
            id = group['id']
            cmpDict[id] = [group, 0]

        for group in newGroups:
            id = group['id']

            if id in cmpDict:
                cmpDict.pop(id)
            else:
                cmpDict[id] = [group, 1]

        changeDict = {
            'new': [],
            'deleted': []
        }

        for item in cmpDict:
            if cmpDict[item][1]:
                changeDict['new'].append(cmpDict[item][0])
            else:
                changeDict['deleted'].append(cmpDict[item][0])

        return changeDict


    def cmpPhotos(self):
        oldPhotos = self._oldInf['photos']['items']
        newPhotos = self._newInf['photos']['items']

        oldPhDict, newPhDict = {}, {}

        for photo in oldPhotos:
            id = photo['photo_id']
            oldPhDict[id] = [photo['comments'], photo['likes']]

        for photo in newPhotos:
            id = photo['photo_id']
            newPhDict[id] = [photo['comments'], photo['likes']]

        listID = []
        changeDict = {
            'new': [],
            'deleted': [],
            'items': []
        }

        for id in oldPhDict:
            if id not in newPhDict:

                oldPh = {
                    'photo_id': id,
                    'comments': oldPhDict[id][0],
                    'likes':    oldPhDict[id][1],
                }

                changeDict['deleted'].append(oldPh)
                listID.append(id)

        for id in listID:
            oldPhDict.pop(id)

        listID = []

        for id in newPhDict:
            if id not in oldPhDict:

                newPh = {
                    'photo_id': id,
                    'comments': newPhDict[id][0],
                    'likes':    newPhDict[id][1],
                }

                changeDict['new'].append(newPh)
                listID.append(id)

        for id in listID:
            newPhDict.pop(id)

        changeLikesList, changeCommList = [], []

        for (old, new) in zip(oldPhDict, newPhDict):
            if oldPhDict[old][0] != newPhDict[new][0]:
                oldComm = oldPhDict[old][0]
                newComm = newPhDict[new][0]

                if oldComm != newComm:
                    cmpDict = {}

                    for item in oldComm['items']:
                        id = item['id']
                        cmpDict[id] = [item, 0]

                    for item in newComm['items']:
                        id = item['id']

                        if id in cmpDict:
                            cmpDict.pop(id)
                        else:
                            cmpDict[id] = [item, 1]

                    for key in cmpDict:

                        if cmpDict[key][1]:
                            cmpDict[key][0]['status'] = 1 #'new comment'
                        else:
                            cmpDict[key][0]['status'] = 0 #'deleted comment'

                        changeCommList.append(cmpDict[key][0])

                oldLikes = oldPhDict[old][1]
                newLikes = newPhDict[new][1]

                if oldLikes != newLikes:
                    cmpDict = {}

                    for item in oldLikes['items']:
                        id = item['id']
                        cmpDict[id] = [item, 0]

                    for item in newLikes['items']:
                        id = item['id']

                        if id in cmpDict:
                            cmpDict.pop(id)
                        else:
                            cmpDict[id] = [item, 1]

                    for key in cmpDict:

                        if cmpDict[key][1]:
                            cmpDict[key][0]['status'] = 1 #'new like'
                        else:
                            cmpDict[key][0]['status'] = 0 #'deleted like'

                        changeLikesList.append(cmpDict[key][0])

                photo = {}
                if not changeCommList:
                    photo['comments'] = changeCommList
                if not changeLikesList:
                    photo['likes'] = changeLikesList
                if (not changeCommList) or (not changeLikesList):
                    photo['photo_id'] = old
                    changeDict['items'].append(photo)

                changeCommList, changeLikesList = [], []

        return changeDict

    def cmpWall(self):
        oldWall = self._oldInf['wall']['items']
        newWall = self._newInf['wall']['items']

        oldWallDict, newWallDict, textDict = {}, {}, {}

        for post in oldWall:
            id = post['post_id']

            textDict[id] = [post['text'], None]
            oldWallDict[id] = [post['comments'], post['likes']]

        for post in newWall:
            id = post['post_id']

            textDict[id] = [None, post['text']]
            newWallDict[id] = [post['comments'], post['likes']]

        listID = []
        changeDict = {
            'new': [],
            'deleted': [],
            'items': []
        }

        for id in oldWallDict:
            if id not in newWallDict:
                oldPost = {
                    'post_id': id,
                    'text': textDict[id][0],
                    'comments': oldWallDict[id][0],
                    'likes': oldWallDict[id][1],
                }

                changeDict['deleted'].append(oldPost)
                listID.append(id)

        for id in listID:
            oldWallDict.pop(id)
            textDict.pop(id)

        listID = []

        for id in newWallDict:
            if id not in oldWallDict:
                newPost = {
                    'post_id': id,
                    'text': textDict[id][1],
                    'comments': newWallDict[id][0],
                    'likes': newWallDict[id][1],
                }

                changeDict['new'].append(newPost)
                listID.append(id)

        for id in listID:
            newWallDict.pop(id)
            textDict.pop(id)

        changeLikesList, changeCommList = [], []

        for (old, new) in zip(oldWallDict, newWallDict):
            if oldWallDict[old][0] != newWallDict[new][0]:
                oldComm = oldPhDict[old][0]
                newComm = newPhDict[new][0]

                if oldComm != newComm:
                    cmpDict = {}

                    for item in oldComm['items']:
                        id = item['id']
                        cmpDict[id] = [item, 0]

                    for item in newComm['items']:
                        id = item['id']

                        if id in cmpDict:
                            cmpDict.pop(id)
                        else:
                            cmpDict[id] = [item, 1]

                    for key in cmpDict:

                        if cmpDict[key][1]:
                            cmpDict[key][0]['status'] = 1 #'new comment'
                        else:
                            cmpDict[key][0]['status'] = 0 #'deleted comment'

                        changeCommList.append(cmpDict[key][0])

                oldLikes = oldWallDict[old][1]
                newLikes = newWallDict[new][1]

                if oldLikes != newLikes:
                    cmpDict = {}

                    for item in oldLikes['items']:
                        id = item['id']
                        cmpDict[id] = [item, 0]

                    for item in newLikes['items']:
                        id = item['id']

                        if id in cmpDict:
                            cmpDict.pop(id)
                        else:
                            cmpDict[id] = [item, 1]

                    for key in cmpDict:

                        if cmpDict[key][1]:
                            cmpDict[key][0]['status'] = 1 #'new like'
                        else:
                            cmpDict[key][0]['status'] = 0 #'deleted like'

                        changeLikesList.append(cmpDict[key][0])

                photo = {}
                if not changeCommList:
                    photo['comments'] = changeCommList
                if not changeLikesList:
                    photo['likes'] = changeLikesList
                if (not changeCommList) or (not changeLikesList):
                    photo['photo_id'] = old
                    changeDict['items'].append(photo)

                changeCommList, changeLikesList = [], []

        print(changeDict)
        return changeDict

    def getChanges(self):
        if self._oldInf is None or self._newInf is None:
            raise Exception('user information was not loaded')

        changeDict = {
            'main_info': self.cmpMainInfo(),
            'friends':   self.cmpFriends(),
            'followers': self.cmpFollowers(),
            'groups':    self.cmpGroups(),
            'photos':    self.cmpPhotos(),
            'wall':      self.cmpWall(),
            'domain':    self._newInf['main_info']['domain'],
            'id':        self._newInf['main_info']['id'],
        }

        return changeDict


if __name__ == '__main__':
    pass

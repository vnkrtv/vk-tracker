import VK_UserInfo


class VK_UserAnalizer:
    def __init__(self, domain):
        self._user = VK_UserInfo(domain)


    def getInfo(self, date):
        pass


    def cmpMainInfo(self):
        oldMain = self.oldInf['main_info']
        newMain = self.newInf['main_info']

        pass


    def cmpFriends(self):
        oldFriends = self.oldInf['friends']['items']
        newFriends = self.newInf['friends']['items']

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

        changeList = []

        for item in cmpDict:
            if cmpDict['item'][1]:
                cmpDict['item'][0]['status'] = 'new friend'
            else:
                cmpDict['item'][0]['status'] = 'deleted from friends'

            changeList.append(cmpDict['item'][0])

        return changeList


    def cmpFollowers(self):
        oldFollowers = self.oldInfo['followers']['items']
        newFollowers = self.newInfo['followers']['items']

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

        changeList = []

        for item in cmpDict:
            if cmpDict['item'][1]:
                cmpDict['item'][0]['status'] = 'new friend'
            else:
                cmpDict['item'][0]['status'] = 'deleted from friends'

            changeList.append(cmpDict['item'][0])

        return changeList


    def cmpGroups(self):
        oldGroups = self.oldInf['groups']['items']
        newGroups = self.newInf['groups']['items']

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

        changeList = []

        for item in cmpDict:
            if cmpDict['item'][1]:
                cmpDict['item'][0]['status'] = 'new friend'
            else:
                cmpDict['item'][0]['status'] = 'deleted from friends'

            changeList.append(cmpDict['item'][0])

        return changeList


    def cmpPhotos(self):
        oldPhotos = self.oldInf['photos']['items']
        newPhotos = self.newInf['photos']['items']

        oldPhDict, newPhDict = {}, {}

        for photo in oldPhotos:
            id = photo['photo_id']
            oldPhDict[id] = [photo['comments'], photo['likes']]

        for photo in newPhotos:
            id = photo['photo_id']
            newPhDict[id] = [photo['comments'], photo['likes']]

        changeList, listID = [], []

        for id in oldPhDict:
            if id in newPhDict:

                oldPh = {
                    'photo_id': id,
                    'comments': oldPhDict[id][0],
                    'likes':    oldPhDict[id][1],
                    'status':   'deleted photo'
                }

                changeList.append(oldPh)
                listID.append(id)

        for id in listID:
            oldPhDict.pop(id)

        listID = []

        for id in newPhDict:
            if id in oldPhDict:

                newPh = {
                    'photo_id': id,
                    'comments': newPhDict[id][0],
                    'likes':    newPhDict[id][1],
                    'status':   'new photo'
                }

                changeList.append(newPh)
                listID.append(id)

        for id in listID:
            newPhDict.pop(id)

        changeLikesList, changeCommList = [], []

        for (old, new) in (oldPhDict, newPhDict):
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
                            cmpDict[key][0]['status'] = 'new comment'
                        else:
                            cmpDict[key][0]['status'] = 'deleted comment'

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
                            cmpDict[key][0]['status'] = 'new like'
                        else:
                            cmpDict[key][0]['status'] = 'deleted like'

                        changeLikesList.append(cmpDict[key][0])

                photo = {}
                if not changeCommList:
                    photo['comments'] = changeCommList
                if not changeLikesList:
                    photo['likes'] = changeLikesList
                if (not changeCommList) or (not changeLikesList):
                    photo['photo_id'] = old
                    changeList.append(photo)

                changeCommList, changeLikesList = [], []

        return changeList


def cmpWall(self):
    oldWall = self.oldInf['wall']['items']
    newWall = self.newInf['wall']['items']

    oldWallDict, newWallDict, textDict = {}, {}, {}

    for post in oldWall:
        id = post['post_id']

        textDict[id] = [post['text'], None]
        oldWallDict[id] = [post['comments'], post['likes']]

    for post in newWall:
        id = post['post_id']

        textDict[id] = [None, post['text']]
        newWallDict[id] = [post['comments'], post['likes']]

    changeList, listID = [], []

    for id in oldWallDict:
        if id in newWallDict:

            oldPost = {
                'post_id':  id,
                'text':     textDict[id],
                'comments': oldWallDict[id][0],
                'likes':    oldWallDict[id][1],
                'status':   'deleted photo'
            }

            changeList.append(oldPh)
            listID.append(id)

    for id in listID:
        oldWallDict.pop(id)
        textDict.pop(id)

    listID = []

    for id in newWallDict:
        if id in oldWallDict:

            newPost = {
                'post_id':  id,
                'text':     textDict[id],
                'comments': newWallDict[id][0],
                'likes':    newWallDict[id][1],
                'status':   'new photo'
            }

            changeList.append(newPh)
            listID.append(id)

    for id in listID:
        newWallDict.pop(id)
        textDict.pop(id)

    changeLikesList, changeCommList = [], []

    for (old, new) in (oldWallDict, newWallDict):
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
                        cmpDict[key][0]['status'] = 'new comment'
                    else:
                        cmpDict[key][0]['status'] = 'deleted comment'

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
                        cmpDict[key][0]['status'] = 'new like'
                    else:
                        cmpDict[key][0]['status'] = 'deleted like'

                    changeLikesList.append(cmpDict[key][0])

            photo = {}
            if not changeCommList:
                photo['comments'] = changeCommList
            if not changeLikesList:
                photo['likes'] = changeLikesList
            if (not changeCommList) or (not changeLikesList):
                photo['photo_id'] = old
                changeList.append(photo)

            changeCommList, changeLikesList = [], []

    return changeList

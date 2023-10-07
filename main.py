import pickle
import numpy as np

from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

class HelloWorld(Resource):
    def __init__(self) -> None:
        self.ds = pickle.load(open('popular.pkl', 'rb'))
        
    def get(self):
        return {
            'titles' : list(self.ds['Book-Title'].values),
            'authors' : list(self.ds['Book-Author'].values),
            'votes' : self.ds['Num-Rating'].tolist(),
            'rating': self.ds['Avg-Rating'].tolist(),
            'images': list(self.ds['Image-URL-L'].values)
            }
    
class Recommender(Resource):
    def __init__(self) -> None:
        self.ds = pickle.load(open('books_ds.pkl', 'rb'))
        self.pt = pickle.load(open('pt.pkl', 'rb'))
        self.ss = pickle.load(open('similarity_scores.pkl', 'rb'))
        
    def get(self, name):
        index = np.where(self.pt.index==name)
        print(index[0])
        if(len(index[0]) == 0):
            return []
        index = np.where(self.pt.index==name)[0][0]
        similar_items = sorted(list(enumerate(self.ss[index])), key=lambda x:x[1], reverse=True)[1:6]
        
        data = []
        for x, y in similar_items:
            item = []
            temp = self.ds[self.ds['Book-Title'] == self.pt.index[x]]
            temp = temp.drop_duplicates('Book-Title')
            item.extend(temp['Book-Title'].values)
            item.extend(temp['Book-Author'].values)
            item.extend(temp['Image-URL-L'].values)
            item.extend([int(value) for value in temp['Num-Rating'].values])
            item.extend(temp['Avg-Rating'].values.astype(float))
            
            data.append(item)
        print(data)
        return data

api.add_resource(HelloWorld, '/')
api.add_resource(Recommender, '/search/<string:name>')

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/Playlister')
client = MongoClient(host=host)
db = client.get_default_database()
playlists = db.playlists
comments = db.comments

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('templates/home.html')

def video_url_creator(id_list):
  videos = []
  for vid_id in id_list:
    video = 'https://youtube.com/embed/' + vid_id
    videos.append(video)
  return videos

@app.route('/')
def playlists_index():
  """ Show all playlists """
  return render_template('playlists_index.html', playlists=playlists.find())

@app.route('/playlists/new')
def playlists_new():
  """ Create a new playlist """
  playlist = []
  return render_template('playlists_new.html', playlist=playlist, title="New Playlist")

@app.route('/playlists', methods=['POST'])
def playlists_submit():
  """ Submit a new playlist """
  video_ids = request.form.get('video_ids').split()
  videos = video_url_creator(video_ids)
  playlist = {
    'title': request.form.get('title'),
    'description': request.form.get('description'),
    'videos': videos,
    'video_ids': video_ids
  }
  playlists.insert_one(playlist)
  return redirect(url_for('playlists_index'))

@app.route('/playlists/<playlist_id>')
def playlists_show(playlist_id):
  """ Show a single playlist """
  playlist = playlists.find_one({'_id': ObjectId(playlist_id)})
  playlist_comments = comments.find({'playlist_id': playlist_id})
  return render_template('playlists_show.html', playlist=playlist, comments=playlist_comments)

@app.route('/playlists/<playlist_id>/edit')
def playlists_edit(playlist_id):
  """ Show the edit form for the playlist """
  playlist = playlists.find_one({'_id': ObjectId(playlist_id)})
  return render_template('playlists_edit.html', playlist=playlist, title='Edit Playlist')

@app.route('/playlists/<playlist_id>', methods=['POST'])
def playlists_update(playlist_id):
  """ Submit an edited playlist """
  video_ids = request.form.get('video_ids').split()
  videos = video_url_creator(video_ids)
  # create our updated playlist
  updated_playlist = {
    'title': request.form.get('title'),
    'description': request.form.get('description'),
    'videos': videos,
    'video_ids': video_ids,
  }
  # set the former playlist to the new one we just updated/edited
  playlists.update_one(
    {'_id': ObjectId(playlist_id)},
    {'$set': updated_playlist})
  # take us ack to the playlist's show page
  return redirect(url_for('playlists_show', playlist_id=playlist_id))

@app.route('/playlists/<playlist_id>/delete', methods=['POST'])
def playlists_delete(playlist_id):
  """ Delete one playlist """
  playlists.delete_one({'_id': ObjectId(playlist_id)})
  return redirect(url_for('playlists_index'))

@app.route('/playlists/comments', methods=['POST'])
def comments_new():
  """ Submit a new comment """
  comment = {
    'playlist_id': request.form.get('playlist_id'),
    'title': request.form.get('title'),
    'content': request.form.get('content'),
  }
  comments.insert_one(comment)
  return redirect(url_for('playlists_show', playlist_id=request.form.get('playlist_id')))

@app.route('/playlists/<playlist_id>/comments/<comment_id>/delete')
def delete_comment(playlist_id, comment_id):
  """ Delete a comment """
  comments.delete_one({'_id': ObjectId(comment_id)})
  return redirect(url_for('playlists_show', playlist_id=playlist_id))

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))

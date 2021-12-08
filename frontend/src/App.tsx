import React, {useEffect, useState} from 'react';
import _ from 'lodash';
import './App.css';
import {statsType, Suggestion, suggestionToApply} from "./types";
import SongInstance from "./SongInstance";

const URLS = {
    "login": "http://localhost:8080/login", // TODO nice maken voor dev vs prod
    "checkLogin": "/checklogin",
    "enable": "/enable",
    "stats": "/stats",
    "songs": "/songs",
    "playlists": "/playlists",
    "apply": "/apply"
}

function App() {
    const [loggedIn, setLoggedIn] = useState(false)
    const [enabled, setEnabled] = useState(false)
    const [error, setError] = useState("")
    // TODO merge these three states
    const [stats, setStats] = useState<statsType[][] | undefined>()
    const [suggestions, setSuggestions] = useState<suggestionToApply[]>([])
    const [markedForApply, setMarkedForApply] = useState<statsType[]>([])

    const addSuggestion = (suggestion: suggestionToApply, stats: statsType) => {
        setSuggestions([...suggestions, suggestion])
        setMarkedForApply([...markedForApply, stats])
    }

    useEffect(() => {
        (async () => {
            // Check if the user is already logged in
            const loggedIn = await checkLogin()
            setLoggedIn(loggedIn)
            if (loggedIn) {
                // Check if the user has enabled tracking
                setEnabled(await checkEnabled())
            }
        })().catch(setError)
    }, [])

    useEffect(() => {
        if (enabled) {
            (async () => {
                const stats = await getStats()
                setStats(stats)
            })()
        }
    }, [enabled])

    if (!loggedIn) {
        return (
            <div className="App">
                <header className="App-header">
                    <a href={URLS.login}>Login with Spotify</a>
                </header>
            </div>
        );
    }

    if (!enabled) {
        return (
            <div className="App">
                <header className="App-header">
                    <p>{error}</p>
                    <button onClick={() => enable().catch(setError).then()}>
                        Start tracking my Spotify account
                    </button>
                </header>
            </div>
        )
    }

    return (
        <div className="App">
            <header className="App-header">
                <p>{error}</p>
                {stats ? stats.map(playlist => {
                        return (<div>
                            <span>{playlist[0].playlist_title}</span> {
                            playlist.map((stats, i) => {
                                const suggestion = calculateSuggestion(stats.listen_count, stats.skip_count)

                                return suggestion ? (<SongInstance
                                    stats={stats} key={i}
                                    apply={addSuggestion}
                                    suggestion={suggestion}
                                    markedForApply={false}
                                />) : null
                            })
                        }</div>)
                    })
                    : ""}
            </header>
        </div>
    );
}

async function checkLogin() {
    const res = await fetch(URLS.checkLogin)
    return res.status === 204
}

async function checkEnabled() {
    const res = await fetch(URLS.enable)
    return await res.json()
}

async function enable() {
    return fetch(URLS.enable, {method: "POST"})
}

async function getStats() {
    const stats: statsType[] = await (await fetch(URLS.stats)).json()
    // Group the songs per playlist
    const groupedStats = _.groupBy(stats, item => item.playlist_id)
    // Change the Dictionary to an array
    return _.values(groupedStats)
}

function calculateSuggestion(listenCount: number, skipCount: number) {
    // TODO check if the song was already in the playlist do determine add vs remove
    if (skipCount / listenCount >= 0.3) {
        return Suggestion.Remove
    }
}

export default App;

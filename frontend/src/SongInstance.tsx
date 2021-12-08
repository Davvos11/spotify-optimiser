import {statsType, Suggestion, suggestionToApply} from "./types";
import React from "react";
import styles from "./styles.module.css"

function SongInstance(
    props: {
        stats: statsType,
        markedForApply: boolean,
        suggestion: Suggestion,
        apply: (suggestion: suggestionToApply, stats: statsType) => void
    }) {

    // Create the suggestion object and a function to add it to the list
    const suggestion: suggestionToApply = {
        playlist_id: props.stats.playlist_id,
        playlist_name: undefined, /* TODO add to new playlist */
        suggestion: props.suggestion,
        track_id: props.stats.track_id
    }
    const onButtonClick = () => props.apply(suggestion, props.stats)

    let button = <></>
    switch (props.suggestion) {
        case Suggestion.Add:
            button = <button className={`${styles.add} ${props.markedForApply ? styles.marked : ''}`}>
                {props.markedForApply ? "Add" : "Add?"}
            </button>
            break;
        case Suggestion.Remove:
            button = <button className={`${styles.remove} ${props.markedForApply ? styles.marked : ''}`}>
                {props.markedForApply ? "Remove" : "Remove?"}
            </button>
            break;
    }

    return (<div className={styles.song}>
        <div className={styles.coverArt}>
            <img src={props.stats.cover_art} alt={props.stats.title}/>
        </div>
        <div className={styles.songInformation}>
            <span>{props.stats.title}</span>
            <span>{props.stats.artists}</span>
        </div>
        <div className={styles.songStats}>
            <span>Played: {props.stats.listen_count}x</span>
            <span>Skipped: {props.stats.skip_count}x</span>
            {button /* TODO add to new playlist button */}
        </div>
    </div>)
}

export default SongInstance
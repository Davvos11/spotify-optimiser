export type statsType = {
    artists: string
    cover_art: string
    listen_count: number
    playlist_id: string
    playlist_title: string
    skip_count: number
    title: string
    track_id: string
    user: {
        enabled: boolean
        user_id: number
    }
}

export enum Suggestion {
    Add,
    Remove,
    AddToNew
}

export type suggestionToApply = {
    playlist_id: string | undefined, // undefined in case of Suggestion.AddToNew
    playlist_name: string | undefined // string in case of Suggestion.AddToNew, otherwise undefined
    track_id: string,
    suggestion: Suggestion
}
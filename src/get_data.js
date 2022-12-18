import { Client, auth } from "twitter-api-sdk";

// Initialize auth client first
// const authClient = new auth.OAuth2User({
//     client_id: process.env.CLIENT_ID,
//     client_secret: process.env.CLIENT_SECRET,
//     callback: "YOUR-CALLBACK",
//     scopes: ["tweet.read", "users.read", "offline.access"],
// });

// Pass auth credentials to the library client 
const client = new Client(process.env.BEARER_TOKEN);
const paramsFollowers = {
    "user.fields": "public_metrics,verified",
}
const paramsTweets = {
    "max_results": 100
}


export const getFollowers = async () => {
    try {
        const userObj = await client.users.findUserByUsername("pj_sekai", paramsFollowers);
        console.log("Data received at " + new Date().toISOString().slice(0, -2));
        return userObj;
    } catch (error) {
        console.log("twitter api get request error", error);
    }
}

export const getTweets = async (id) => {
    try {
        const tweetObj = await client.tweets.usersIdTweets(id, paramsTweets);
        console.log("Data received at " + new Date().toISOString().slice(0, -2));
        return tweetObj;
    } catch (error) {
        console.log("twitter api get request error");
        thorw(error)
    }
}
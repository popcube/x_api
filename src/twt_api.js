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
    "max_results": 100,
    "tweet.fields": "created_at,id,public_metrics,text,withheld,referenced_tweets"
}


export const getFollowers = async (userName) => {
    try {
        const userObj = await client.users.findUserByUsername(userName, paramsFollowers);
        // console.log(JSON.stringify(userObj))
        console.log("Followers data received at " + new Date().toISOString().slice(0, -2));
        return userObj;
    } catch (error) {
        console.log("twitter api findUserByUsername request error");
        throw (error);
    }
}

export const getTweets = async (id, paginate = false) => {
    try {
        delete paramsTweets["pagination_token"];
        var tweetObj = await client.tweets.usersIdTweets(id, paramsTweets);
        // console.log(tweetObj);
        const resArr = tweetObj.data;
        console.log("Tweets data received at " + new Date().toISOString().slice(0, -2));
        // console.log("meta: " + JSON.stringify(tweetObj.meta, null, 2))
        if (paginate) {
            while (tweetObj.meta.next_token) {
                paramsTweets["pagination_token"] = tweetObj.meta.next_token;
                var tweetObj = await client.tweets.usersIdTweets(id, paramsTweets);
                resArr.push(...tweetObj.data);
                console.log("paginating... until tweets created at " + tweetObj.data[tweetObj.data.length - 1].created_at);
            }
        }
        return resArr;
    } catch (error) {
        console.log("twitter api usersIdTweets request error");
        throw (error);
    }
}
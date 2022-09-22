const {merge} = require("webpack-merge");
const common = require("./webpack.common.js");
const TerserPlugin = require('terser-webpack-plugin');

module.exports = merge(common, {

    module: {
        rules: [
            {
                test: /\.m?js$/,
                exclude: /(node_modules|bower_components)/,
                use: [
                    {
                        loader: "stripcomment-loader"
                    }
                ]
            }
        ]
    },

    optimization: {
        minimize: true,
        concatenateModules: false,
        minimizer: [
            new TerserPlugin({
                terserOptions: {
                    compress: {
                        defaults: false,
                        drop_console: true
                    },
                    output: {
                        comments: false,
                        beautify: true
                    },
                    keep_classnames: true,
                    keep_fnames: true
                },
                extractComments: false
            })
        ]
    }

});

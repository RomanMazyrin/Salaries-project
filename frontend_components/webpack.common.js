const path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {

    mode : process.env.NODE_ENV,

    output: {
        filename: 'Components.js',
        path: path.resolve(__dirname, 'dist'),
        libraryTarget: 'umd',
        umdNamedDefine: true
    },

    devtool: false,

    module: {
        rules: [
            {
                test: /\.m?jsx?$/,
                exclude: /node_modules/,
                use: [
                    {
                        loader: 'babel-loader'
                    }
                ]
            },
            {
                test: /\.css$/,
                use: [
                    'style-loader',
                    'css-loader'
                ]
            },
            {
                test: /\.s[ac]ss$/i,
                use: [
                    'style-loader',
                    'css-loader',
                    "sass-loader",
                ],
            }
        ]
    },

    resolve: {
		extensions: ['.js', '.jsx', '.json', '.riot', '.css', '.scss', '.gif']
	},

    plugins: [
        new CleanWebpackPlugin()
    ]
};

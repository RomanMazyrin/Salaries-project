const path = require('path');

module.exports = {

    mode : process.env.NODE_ENV,

    output: {
        filename: 'Components.js',
        path: path.resolve(__dirname, '../src/salaries/static/salaries/js'),
        library: {
            name: 'MyLibrary',
            type: 'var',
        },
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
    ]
};

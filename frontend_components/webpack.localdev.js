const {merge} = require("webpack-merge");
const common = require("./webpack.common.js");
const HTMLWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const path = require("path");

const config = merge(common, {
    context: path.resolve(__dirname, 'local'),
	entry: {
		main: ['./index.js']
	},
	output: {
		filename: '[name].js',
		path: path.resolve(__dirname, 'dist')
	},

	module: {
        rules: [
            {
                test: /\.(png|jpe?g|gif)$/i,
				use: [
					{
						loader: 'file-loader',
					},
				],
            },
		]
	},
	
	resolve: {
		extensions: ['.js', '.jsx', '.json', '.riot', '.css', '.scss', '.gif']
	},

	devServer: {
        port: 8080,
        hot: true
    },

	plugins: [
		new HTMLWebpackPlugin({
			template: './index.html',
			minify: {
				collapseWhitespace: false
			}
		})
	]
});

config.plugins = config.plugins.filter(plugin => !['MiniCssExtractPlugin', "WebpackOnBuildPlugin"].includes(plugin.constructor.name));
config.plugins.push(new MiniCssExtractPlugin({
	filename: '[name].css'
}));

module.exports = config;
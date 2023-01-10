

class make_js:

    output_js = ""

    def __init__(self, js_name):
        self.output_js = f'./{js_name}.js'
        with open(self.output_js, "w") as f:
            f.write("const twt_data = [\n")

    def __del__(self):
        with open(self.output_js, "a") as f:
            f.writelines([
                "];\n",
                "export default twt_data;\n"
            ])

    def write_js(self, in_ds, data_name):

        data_count = len(in_ds)
        with open(self.output_js, "a") as f:
            f.writelines([
                "    {\n",
                '        name: "' + data_name + '",\n',
                "        x: [\n",
                "            "
            ])
            f.writelines(in_ds.index.to_series().apply(
                self.timestamp_to_str).to_list())
            f.writelines([
                "\n",
                "        ],\n",
                "        y: [\n",
                "            "
            ])
            f.writelines(in_ds.apply(lambda x: f'{x}, ').to_list())
            f.writelines([
                "\n",
                "        ],\n",
                "    },\n"
            ])
            print(f'{data_count} data are written')

    @staticmethod
    def timestamp_to_str(ts):
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        return f'"{ts_str}", '

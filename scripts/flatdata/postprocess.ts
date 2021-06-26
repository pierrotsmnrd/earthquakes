//import 'https://deno.land/x/flat@0.0.10/mod.ts'


// install requirements with pip
const pip_install = Deno.run({
    cmd: ['python', '-m', 'pip', 'install', 'pandas'],
});

await pip_install.status();



// Forwards the execution to the python script
const py_run = Deno.run({
    cmd: ['python', './scripts/flatdata/postprocessing.py'].concat(Deno.args),
});

await py_run.status();

import JSON

function load_sound_classes(filename::String)::Dict
    class_file = open(filename, "r")
    content = read(class_file, String)
    close(class_file)

    sound_class = Dict{String, String}()

    content = JSON.parse(content)

    for class in get(content, "classes", Dict())
        for phone in get(class, "phones", "")
            sound_class[phone] = get(class, "label", "")
        end
    end
    return sound_class
end

function ipa_to_array(
    word::String,
    sound_class::Dict{String, String},
    composites::Dict)::Array{String, 1}

    sounds = keys(sound_class)

    for i in keys(composites)
        word = replace(word, i => get(composites, i, i))
    end

    word_array = Array{String, 1}()
    word_array = [string(c) for c in word
        if string(c) in sounds || string(c) in values(composites)]

    for i in eachindex(word_array)
        if word_array[i] in values(composites)
            key = ""
            for (k, v) in composites
                if v == word_array[i]
                    key = k
                    break
                end
            end
            word_array[i] = key
        end
    end

    return word_array
end

function array_to_classes(word::Array{String, 1})::String
    return join([get(sound_class, c, "") for c in word])
end

sound_class = load_sound_classes("./classes.json")
comp = Array{String, 1}()

a = 0
comp = Dict()
for c in keys(sound_class)
    if occursin("͡", c)
        comp[c] = string(a)
        global a = a + 1 
    end
end

words = ["kʷeɾno", "bæt͡ʃ"]
for word in words
    array = ipa_to_array(word, sound_class, comp)
    println(array)
    println(array_to_classes(array))
end
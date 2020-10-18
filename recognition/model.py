import tensorflow as tf
import numpy as np

def context_layer(input, channels):
    context_1 = tf.keras.layers.Conv2D(channels, (3, 3), activation="relu", padding="same")(input)
    context_dropout = tf.keras.layers.Dropout(0.3)(context_1)
    context_2 = tf.keras.layers.Conv2D(channels, (3, 3), activation="relu", padding="same")(context_dropout)
    return context_2

def decode_layer(input, channels):
    decode_1 = tf.keras.layers.Conv2D(channels, (3, 3), strides=(2,2), activation="relu", padding="same")(input)
    context = context_layer(decode_1, channels)
    elem_wise_sum = decode_1 + context
    return elem_wise_sum

def upsampling_module(input, channels):
    up = tf.keras.layers.UpSampling2D()(input)
    conv2d = tf.keras.layers.Conv2D(channels, (3, 3), activation="relu", padding="same")(up)
    return conv2d

def localization_layer(input, channels):
    conv2D_3 = tf.keras.layers.Conv2D(channels, (3, 3), activation="relu", padding="same")(input)
    conv2D_1 = tf.keras.layers.Conv2D(channels, (1, 1), activation="relu", padding="same")(conv2D_3)
    return conv2D_1

def segmentation_layer(input, channels):
    return tf.keras.layers.Conv2D(channels, (1, 1), activation="relu", padding="same")(input)


def improved_unet(output_channels, f=16, input_shape=(256, 256, 1)):
    modelInput = tf.keras.layers.Input(shape=(256, 256, 1))

    conv2D16_1 = tf.keras.layers.Conv2D(f, (3, 3), activation="relu", padding="same")(modelInput)

    #1st Context Layer
    context_16 = context_layer(conv2D16_1, f)

    #Element wise sum
    elem_wise_sum_16 = conv2D16_1 + context_16

    d1 = decode_layer(elem_wise_sum_16, 2*f)

    d2 = decode_layer(d1, 4*f)

    d3 = decode_layer(d2, 8*f)

    d4 = decode_layer(d3, 16*f)

    u128 = upsampling_module(d4, 8*f)

    concat1 = tf.keras.layers.Concatenate()([u128, d3])

    local_layer_128 = localization_layer(concat1, 8*f)

    u64 = upsampling_module(local_layer_128, 4*f)

    concat2 = tf.keras.layers.Concatenate()([u64, d2])

    local_layer_64 = localization_layer(concat2, 4*f)

    seg64 = segmentation_layer(local_layer_64, output_channels)

    u32 = upsampling_module(local_layer_64, 2*f)

    concat3 = tf.keras.layers.Concatenate()([u32, d1])

    local_layer_32 = localization_layer(concat3, 2*f)

    seg32 = segmentation_layer(local_layer_32, output_channels)

    u16 = upsampling_module(local_layer_32, f)

    concat4 = tf.keras.layers.Concatenate()([u16, elem_wise_sum_16])

    conv2d_32 = tf.keras.layers.Conv2D(2*f, (3, 3), activation="relu", padding="same")(concat4)

    seg32_1 = segmentation_layer(conv2d_32, output_channels)

    seg64_upscaled = tf.keras.layers.UpSampling2D()(seg64)

    elemwise_sum_seg1 = seg64_upscaled + seg32

    seg32_upscaled = tf.keras.layers.UpSampling2D()(elemwise_sum_seg1)

    segment = seg32_1 + seg32_upscaled

    output = tf.keras.layers.Conv2D(4, (1, 1), activation="softmax", padding="same")(segment)

    model = tf.keras.Model(inputs=modelInput, outputs=output)
    return model


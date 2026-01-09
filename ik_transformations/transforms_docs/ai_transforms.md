Below is **only for `e-removedotbg`**, written exactly in the structure you asked for and **using examples strictly from the doc**.

---

## Description

**`e-removedotbg`**
Removes the background from an image using AI, producing a transparent background around the primary subject.

---

## Limitations


---

## Examples

Below is **only for `e-bgremove`**, structured exactly as requested and **using examples strictly from the documentation you shared**.

---

## Description

**`e-bgremove`**
Removes the background from an image using ImageKit’s AI-powered background removal, offering a more cost-efficient alternative to `e-removedotbg`.

---

## Limitations

* This is an **AI transformation** and may take longer than basic transformations.
* The output may return an **intermediate HTML response** with status `200` and header `is-intermediate-response:true` if processing is still ongoing.
* Only **one async AI transformation** is allowed per transformation step; multiple AI transformations must be **chained using `:`**, not combined with `,`.
* If a request fails, the error response is **cached for a short duration**; retrying the same URL may require waiting a few minutes.
* Outputs are **cached indefinitely** to prevent repeated extension unit consumption.
* Can be used inside **image overlay layers** (exception to the general AI transformation restriction).
* Consumes **extension units**, but at a significantly lower cost compared to `e-removedotbg` (approximately 1/10th).

---

## Examples

### Example 1: Remove background from an image

This example shows how to remove the background from an image using the `e-bgremove` transformation.

```
{
  "tr": "e-bgremove"
}
```

---

### Example 2: Remove background and add a drop shadow using chained transformations

This example shows how to remove the background first and then add a drop shadow by chaining AI transformations using a colon (`:`).

```
{
  "tr": "e-bgremove:e-dropshadow"
}
```

---

## Details and Examples Using Other Parameters

### Chaining with AI drop shadow

This example demonstrates combining `e-bgremove` with another AI transformation by placing them in **separate chained steps**.

```
{
  "tr": "e-bgremove:e-dropshadow"
}
```

---

### Usage inside image overlay layers

This example highlights that `e-bgremove` can be used inside image overlay layers, unlike most AI transformations.

```
{
  "tr": "e-bgremove"
}
```


## Description

**`e-dropshadow`**
Adds an AI-generated drop shadow around the main object in an image, simulating realistic lighting based on a virtual light source.

---

## Limitations

* The image **must have a transparent background** for the drop shadow to be visible.
* Background transparency is typically achieved using `e-removedotbg` **before** applying `e-dropshadow`.
* This is an **AI transformation** and may take longer than basic effects.
* The response may be an **intermediate HTML response** with status `200` and header `is-intermediate-response:true` while processing.
* Only **one async AI transformation** is allowed per transformation step.

  * Multiple AI transformations must be **chained using `:`**, not combined with `,`.
* If a request fails, the error response is **cached briefly**, so retries on the same URL may require waiting.
* Outputs are **cached indefinitely** to prevent repeated extension unit usage.
* Consumes **extension units** as per your pricing plan.
* Can be used inside **image overlay layers** (exception to most AI transformations).

---

## Parameters and Defaults

The following parameters can be used with `e-dropshadow`:

* **`az` (Azimuth)**
  Direction of the light source.
  Range: `0–360`
  Default: `215`

* **`el` (Elevation)**
  Elevation angle of the light source above the surface.
  Range: `0–90`
  Default: `45`

* **`st` (Saturation)**
  Intensity of the shadow.
  Range: `0–100`
  Default: `60`

Syntax:

```
e-dropshadow[:-az-${0-360}][:_el-${0-90}][:_st-${0-100}]
```

---

## Examples

### Example 1: Add AI drop shadow to an image

This example shows how to add a default AI drop shadow to an image with a transparent background.

```
{
  "tr": "e-dropshadow"
}
```

---

### Example 2: Change light source direction using azimuth

This example shows how to change the direction of the light source by setting the azimuth angle.

```
{
  "tr": "e-dropshadow-az-45"
}
```

---

## Details and Examples Using Other Parameters

### Applying drop shadow after background removal

This example shows how to remove the background first and then add a drop shadow by chaining AI transformations.

```
{
  "tr": "e-removedotbg:e-dropshadow"
}
```

---

### Comparison with non-AI shadow effect

This example highlights the difference between AI drop shadow and the regular shadow effect using `e-shadow`.

```
{
  "tr": "e-shadow"
}
```

## Description

**`e-changebg`**
Changes the background of an image by generating a new background based on a descriptive text prompt while preserving the foreground subject.

---

## Limitations

* This is an **AI transformation** and may take longer than standard image transformations.
* The response may be an **intermediate HTML response** with status `200` and header `is-intermediate-response:true` while the background is being generated.
* Only **one async AI transformation** is allowed per transformation step.

  * Multiple AI transformations must be **chained using `:`**, not combined using `,`.
* If a request fails, the error response is **cached temporarily**, and retries on the same URL may require waiting.
* Outputs are **cached indefinitely** to avoid repeated extension unit usage.
* Most AI transformations **cannot be used inside layers**; `e-changebg` is not listed as an exception.
* Consumes **extension units** based on your pricing plan.

---

## Parameters and Defaults

The following parameters are supported with `e-changebg`:

* **`prompt` (text prompt)**
  Describes the new background to be generated.
  Formats:

  * `e-changebg-prompt-${text}`
  * `e-changebg-prompte-${urlencoded_base64_encoded_text}`
    Default: **No default** (required)

There are **no additional configurable sub-parameters** (such as strength, style, or positioning) directly attached to `e-changebg`.

---

## Examples

### Example 1: Change background using a text prompt

This example shows how to replace the background with a snowy road scene using a direct text prompt.

```
{
  "tr": "e-changebg-prompt-snow road"
}
```

---

### Example 2: Change background using a Base64 URL-encoded prompt

This example shows how to replace the background using a Base64 URL-encoded text prompt.

```
{
  "tr": "e-changebg-prompte-cmFjaW5nIHRyYWNr"
}
```

---

## Details and Examples Using Other Parameters

### Resizing and repositioning subject before changing background

This example demonstrates resizing the subject, positioning it in the top-right corner, and placing it on a neutral background before applying the background change.

```
{
  "tr": "h-200:w-1200,h-200,cm-pad_resize,fo-right,bg-CCCCCC:w-1200,h-600,cm-pad_resize,bg-CCCCCC,fo-top"
}
```

---

### Applying background change after layout adjustments

This example shows changing the background after resizing and repositioning using chained transformations.

```
{
  "tr": "h-200:w-1200,h-200,cm-pad_resize,fo-right,bg-CCCCCC:w-1200,h-600,cm-pad_resize,bg-CCCCCC,fo-top:e-changebg-prompt-bathroom"
}
```

---

If you want to continue, the next clean fits in this sequence would be **`e-edit`** or **`bg-genfill`**, which also have prompt variants and stricter parameter requirements.


Below is **only for `e-changebg`**, written **copy-paste ready**, strictly following your structure, and **using only examples present in the documentation you shared**.

---

## Description

**`e-changebg`**
Changes the background of an image by generating a new background based on a descriptive text prompt while preserving the foreground subject.

---

## Limitations

* This is an **AI transformation** and may take longer than standard image transformations.
* The response may be an **intermediate HTML response** with status `200` and header `is-intermediate-response:true` while the background is being generated.
* Only **one async AI transformation** is allowed per transformation step.

  * Multiple AI transformations must be **chained using `:`**, not combined using `,`.
* If a request fails, the error response is **cached temporarily**, and retries on the same URL may require waiting.
* Outputs are **cached indefinitely** to avoid repeated extension unit usage.
* Most AI transformations **cannot be used inside layers**; `e-changebg` is not listed as an exception.
* Consumes **extension units** based on your pricing plan.

---

## Parameters and Defaults

The following parameters are supported with `e-changebg`:

* **`prompt` (text prompt)**
  Describes the new background to be generated.
  Formats:

  * `e-changebg-prompt-${text}`
  * `e-changebg-prompte-${urlencoded_base64_encoded_text}`
    Default: **No default** (required)

There are **no additional configurable sub-parameters** (such as strength, style, or positioning) directly attached to `e-changebg`.

---

## Examples

### Example 1: Change background using a text prompt

This example shows how to replace the background with a snowy road scene using a direct text prompt.

```
{
  "tr": "e-changebg-prompt-snow road"
}
```

---

### Example 2: Change background using a Base64 URL-encoded prompt

This example shows how to replace the background using a Base64 URL-encoded text prompt.

```
{
  "tr": "e-changebg-prompte-cmFjaW5nIHRyYWNr"
}
```

---

## Details and Examples Using Other Parameters

### Resizing and repositioning subject before changing background

This example demonstrates resizing the subject, positioning it in the top-right corner, and placing it on a neutral background before applying the background change.

```
{
  "tr": "h-200:w-1200,h-200,cm-pad_resize,fo-right,bg-CCCCCC:w-1200,h-600,cm-pad_resize,bg-CCCCCC,fo-top"
}
```

---

### Applying background change after layout adjustments

This example shows changing the background after resizing and repositioning using chained transformations.

```
{
  "tr": "h-200:w-1200,h-200,cm-pad_resize,fo-right,bg-CCCCCC:w-1200,h-600,cm-pad_resize,bg-CCCCCC,fo-top:e-changebg-prompt-bathroom"
}
```

Below is **only for `e-edit`**, written **copy-paste ready**, following your structure exactly, and **using only examples explicitly present in the documentation you shared**.

---

## Description

**`e-edit`**
Edits or modifies the contents of an image using a descriptive text prompt, generating a new image with AI-driven visual changes.

---

## Limitations

* This is an **AI transformation** and may take longer than standard image transformations.
* The response may return an **intermediate HTML response** with status `200` and header `is-intermediate-response:true` while processing.
* Only **one async AI transformation** is allowed per transformation step.

  * Multiple AI transformations must be **chained using `:`**, not combined using `,`.
* If a request fails, the error response is **cached for a short duration**, and retries on the same URL may require waiting.
* Outputs are **cached indefinitely** to avoid repeated extension unit usage.
* Most AI transformations **cannot be used inside layers**; `e-edit` is not listed as an exception.
* Consumes **extension units** based on your pricing plan.
* **Output size rules**:

  * If the input image is square → output is `1024 × 1024`
  * Otherwise → output is `1536 × 1024` or `1024 × 1536`
  * The shorter side is padded seamlessly to match the output size.

---

## Parameters and Defaults

The following parameters are supported with `e-edit`:

* **`prompt` (text prompt)**
  Describes how the image should be edited.
  Formats:

  * `e-edit-prompt-${text}`
  * `e-edit-prompte-${urlencoded_base64_encoded_text}`
    Default: **No default** (required)

There are **no additional configurable sub-parameters** (such as strength, mask, or style) available for `e-edit`.

---

## Examples

### Example 1: Edit image using a text prompt

This example shows editing a cake image by adding decorative elements using a direct text prompt.

```
{
  "tr": "e-edit-prompt-add some flair to this plain cake"
}
```

---

### Example 2: Edit image using a Base64 URL-encoded text prompt

This example shows modifying the seawater color using a Base64 URL-encoded prompt.

```
{
  "tr": "e-edit-prompte-bWFrZSB0aGUgc2Vhd2F0ZXIgYmx1ZQo%3D"
}
```

---

## Details and Examples Using Other Parameters

### Using Base64 encoding for special characters

This example demonstrates using the Base64-encoded prompt method when the prompt contains special characters like `/`, `:` or `,`.

```
{
  "tr": "e-edit-prompte-bWFrZSB0aGUgc2Vhd2F0ZXIgYmx1ZQo%3D"
}
```

---

### Output dimension handling

This example highlights that the output dimensions are automatically adjusted and padded based on the input image’s aspect ratio.

```
{
  "tr": "e-edit-prompt-add some flair to this plain cake"
}
```

---

If you want, next I can continue with **`bg-genfill`**, **`e-retouch`**, or **`e-upscale`** in the same strict, schema-friendly format you’re building.

---

Below is **only for `bg-genfill`**, written **copy-paste ready**, following your structure exactly, and **using only examples explicitly present in the documentation you shared**.

---

## Description

**`bg-genfill`**
Extends an image beyond its original boundaries by generating new background content using AI while preserving the original image content.

---

## Limitations

* This is an **AI transformation** and may take longer than standard image transformations.
* The response may return an **intermediate HTML response** with status `200` and header `is-intermediate-response:true` while processing.
* Only **one async AI transformation** is allowed per transformation step.

  * Multiple AI transformations must be **chained using `:`**, not combined using `,`.
* If a request fails, the error response is **cached temporarily**, and retries on the same URL may require waiting.
* Outputs are **cached indefinitely** to avoid repeated extension unit usage.
* Most AI transformations **cannot be used inside layers**; `bg-genfill` is not listed as an exception.
* **Required parameters**:

  * Must be used with **`width (w)`**, **`height (h)`**
  * Must use either **`cm-pad_resize`** or **`cm-pad_extract`**
* Consumes **extension units** based on your pricing plan.

---

## Parameters and Defaults

The following parameters are supported with `bg-genfill`:

* **`prompt` (text prompt)** *(optional)*
  Describes what should be generated in the extended background.
  Formats:

  * `bg-genfill-prompt-${text}`
  * `bg-genfill-prompte-${urlencoded_base64_encoded_text}`
    Default: **No prompt** (AI fills background automatically)

* **`width (w)`** *(required)*
  Target width of the output image.
  Default: **None (required)**

* **`height (h)`** *(required)*
  Target height of the output image.
  Default: **None (required)**

* **`crop_mode (cm)`** *(required)*
  Must be one of:

  * `cm-pad_resize`
  * `cm-pad_extract`
    Default: **None (required)**

There are **no additional AI-specific tuning parameters** for `bg-genfill`.

---

## Examples

### Example 1: Extend image width using generative fill

This example shows extending an image to a width of `1000px` using generative fill.

```
{
  "tr": "bg-genfill,w-1000,h-960,cm-pad_resize"
}
```

---

### Example 2: Extend image width using generative fill with a text prompt

This example shows extending the image while controlling the generated content using a text prompt.

```
{
  "tr": "bg-genfill-prompt-flowers,w-1000,h-960,cm-pad_resize"
}
```

---

## Details and Examples Using Other Parameters

### Using generative fill with padding-based resize strategy

This example demonstrates that `bg-genfill` must be combined with `pad_resize` to expand the canvas.

```
{
  "tr": "bg-genfill,w-1000,h-960,cm-pad_resize"
}
```

---

### Controlling generated background with a prompt

This example shows how a prompt can guide the AI to generate specific elements in the extended background.

```
{
  "tr": "bg-genfill-prompt-flowers,w-1000,h-960,cm-pad_resize"
}
```

---

If you want to continue next, the natural follow-ups in this series would be **`e-retouch`** and **`e-upscale`**, which have strict resolution-based constraints and simpler parameter sets.

Below is **only for `e-retouch`**, written **copy-paste ready**, following your structure exactly, and **using only examples explicitly present in the documentation you shared**.

---

## Description

**`e-retouch`**
Improves the visual quality of an image using AI by enhancing details and correcting imperfections.

---

## Limitations

* This is an **AI transformation** and may take longer than standard image transformations.
* The response may return an **intermediate HTML response** with status `200` and header `is-intermediate-response:true` while processing.
* Only **one async AI transformation** is allowed per transformation step.

  * Multiple AI transformations must be **chained using `:`**, not combined using `,`.
* If a request fails, the error response is **cached for a short duration**, and retries on the same URL may require waiting.
* Outputs are **cached indefinitely** to avoid repeated extension unit usage.
* Most AI transformations **cannot be used inside layers**; `e-retouch` is not listed as an exception.
* **Input image resolution must be less than 16 megapixels (16 MP)**.
* Consumes **extension units** based on your pricing plan.

---

## Parameters and Defaults

The following parameters are supported with `e-retouch`:

* **No additional parameters**
  The transformation is applied as a single flag:
  `e-retouch`
  Default behavior applies automatically.

---

## Examples

### Example 1: Improve image quality using retouch

This example shows improving the quality of a low-quality image using AI retouch.

```
{
  "tr": "e-retouch"
}
```

---

## Details and Examples Using Other Parameters

### Applying retouch as a standalone AI enhancement

This example demonstrates using `e-retouch` without any additional tuning parameters.

```
{
  "tr": "e-retouch"
}
```

---

### Retouch output comparison

This example highlights the improvement in image quality after applying the retouch transformation.

```
{
  "tr": "e-retouch"
}
```

---

If you want, I can continue next with **`e-upscale`** or **`e-genvar`**, which are the last remaining AI transformations from this page.

Below is **only for `e-upscale`**, written **copy-paste ready**, strictly following your structure, and **using only examples explicitly present in the documentation you shared**.

---

## Description

**`e-upscale`**
Increases the resolution of an image using AI, enhancing details while scaling the image up to a higher resolution.

---

## Limitations

* This is an **AI transformation** and may take longer than standard image transformations.
* The response may return an **intermediate HTML response** with status `200` and header `is-intermediate-response:true` while processing.
* Only **one async AI transformation** is allowed per transformation step.

  * Multiple AI transformations must be **chained using `:`**, not combined using `,`.
* If a request fails, the error response is **cached temporarily**, and retries on the same URL may require waiting.
* Outputs are **cached indefinitely** to avoid repeated extension unit usage.
* Most AI transformations **cannot be used inside layers**; `e-upscale` is not listed as an exception.
* **Input image resolution must be less than 16 megapixels (16 MP)**.
* **Output image resolution is always 16 MP**.
* Consumes **extension units** based on your pricing plan.

---

## Parameters and Defaults

The following parameters are supported with `e-upscale`:

* **No additional parameters**
  The transformation is applied as a single flag:
  `e-upscale`
  Default behavior applies automatically.

---

## Examples

### Example 1: Upscale an image using AI

This example shows increasing the resolution of a low-resolution image using the `e-upscale` transformation.

```
{
  "tr": "e-upscale"
}
```

---

## Details and Examples Using Other Parameters

### Upscaling a low-resolution image

This example demonstrates applying `e-upscale` to automatically enhance and increase image resolution.

```
{
  "tr": "e-upscale"
}
```

---

### Output resolution behavior

This example highlights that the output image is automatically scaled to 16 MP regardless of the input size.

```
{
  "tr": "e-upscale"
}
```

---

If you want, the **final remaining AI transformation** from this page is **`e-genvar`** (generate variations). I can do that next in the same strict, schema-friendly format.

---


Below is **only for `ik-genimg`**, written **copy-paste ready**, strictly following your structure, and **using only examples explicitly present in the documentation you shared**.

---

## Description

**`ik-genimg`**
Generates a new image from a text prompt using AI and stores the generated image at the specified file path.

---

## Limitations

* This is an **AI image generation operation** and may take longer than standard image transformations.
* The response may return an **intermediate HTML response** with status `200` and header `is-intermediate-response:true` while the image is being generated.
* Generated images are **cached indefinitely** at the specified file path.
* Changing the prompt **on the same file path will NOT generate a new image**.

  * To generate a new image, you must:

    * Purge the cache for the URL, or
    * Change the file path or filename, or
    * Append a random query parameter.
* Consumes **extension units** based on your pricing plan.
* The generated image must be accessed via a **path-based URL**, not via `?tr=`.
* Can be combined with other **image transformation parameters** after generation.

---

## Parameters and Defaults

The following parameters are supported with `ik-genimg`:

* **`prompt` (text prompt)** *(required)*
  Describes the image to be generated.
  Format:

  * `ik-genimg-prompt-${text}`
    Default: **No default** (required)

* **`filepath` and `filename`** *(required)*
  `ik-genimg-prompt-${text}/filepath/filename.jpg`
  Determines where the generated image will be stored and accessed.
  Default: **None (required)**

There are **no additional AI tuning parameters** (such as style, seed, or resolution) available for `ik-genimg`.

---

## Examples

### Example 1: Generate an image using a text prompt

This example shows generating an image of a man eating a burger.

```
{
  "path": "ik-genimg-prompt-A man eating a burger/gen-burger-image.jpg"
}
```

---

### Example 2: Generate another version by appending a query parameter

This example shows forcing regeneration by appending a random query parameter.

```
{
  "path": "ik-genimg-prompt-A man eating a burger/gen-burger-image.jpg",
  "query": "v=3"
}
```

---

### Example 3: Generate an image using a different prompt and path

This example shows generating an image of a woman wearing a red top using a different path.

```
{
  "path": "ik-genimg-prompt-A woman wearing red top/gen-woman-red-top.jpg"
}
```

---

## Details and Examples Using Other Parameters

### Removing background from a generated image and resizing it

This example demonstrates applying additional image transformations after generating the image.

```
{
  "tr": "e-removedotbg,w-500"
}
```

---

### Adding a text overlay layer on a generated image

This example shows adding a text overlay layer to a generated image.

```
{
  "tr": "w-500,l-text,i-30%%20off,fs-45,lfo-top_left,pa-10,bg-white,l-end"
}
```

---

### Combining generation and transformations

This example highlights that `ik-genimg` generates the image first, after which normal image transformations can be applied using `?tr=`.

```
{
  "path": "ik-genimg-prompt-A woman wearing red top/gen-woman-red-top.jpg",
  "tr": "w-500"
}
```

---

If you want, the **last remaining AI transformation** from this page is **`e-genvar`**, and then you’ll have a complete, uniform schema covering every AI transformation in the doc.

Below is **only for `e-genvar`**, written **copy-paste ready**, strictly following your structure, and **using only examples explicitly present in the documentation you shared**.

---

## Description

**`e-genvar`**
Generates AI-based visual variations of an existing image while preserving its overall structure and composition.

---

## Limitations

* This is an **AI transformation** and may take longer than standard image transformations.
* The response may return an **intermediate HTML response** with status `200` and header `is-intermediate-response:true` while processing.
* Only **one async AI transformation** is allowed per transformation step.

  * Multiple AI transformations must be **chained using `:`**, not combined using `,`.
* If a request fails, the error response is **cached temporarily**, and retries on the same URL may require waiting.
* Outputs are **cached indefinitely** to avoid repeated extension unit usage.
* Most AI transformations **cannot be used inside layers**; `e-genvar` is not listed as an exception.
* Consumes **extension units** based on your pricing plan.
* Variations are **non-deterministic**; generating another variation requires changing the URL (e.g., adding a query parameter).

---

## Parameters and Defaults

The following parameters are supported with `e-genvar`:

* **No additional parameters**
  The transformation is applied as a single flag:
  `e-genvar`
  Default behavior applies automatically.

---

## Examples

### Example 1: Generate a variation of an image

This example shows generating a variation of an image after resizing it.

```
{
  "tr": "w-600,h-400:e-genvar"
}
```

---

### Example 2: Generate another variation using a query parameter

This example shows forcing generation of a different variation by appending a random query parameter.

```
{
  "tr": "w-600,h-400:e-genvar",
  "query": "v=3"
}
```

---

## Details and Examples Using Other Parameters

### Combining resize and variation generation

This example demonstrates resizing an image before generating a variation.

```
{
  "tr": "w-600,h-400:e-genvar"
}
```

---

### Comparing original and generated variation

This example highlights the difference between the original resized image and its AI-generated variation.

```
{
  "tr": "w-600,h-400"
}
```

---

At this point, you now have **schema-consistent, copy-paste-ready definitions for every AI transformation** covered in the document.
If you want, next I can:

* Convert all of these into **YAML / JSON schemas**
* Add **validation rules (requires / conflicts / chaining rules)**
* Normalize them into a **single transformation registry** usable directly by your LLM or tool layer

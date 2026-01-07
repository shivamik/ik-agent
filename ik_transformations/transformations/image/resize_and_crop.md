Got it. Below is a **systematic, example-driven reference** showing **how each transformation is expressed in the `transformation` dict passed to `build_url()`**, based on your `SUPPORTED_TRANSFORMS` mapping and ImageKit URL semantics.

I’ll follow these rules consistently:

* **Keys** → use the *friendly keys* from your mapping (`width`, `crop`, `focus`, etc.)
* **Values** → what the developer actually passes
* **No-value flags** → passed as a **string enum** (not `True`)
* **Arithmetic expressions** → passed as strings
* **Examples are minimal and composable**

---

## 1. Width & Height

### `w` — width (number or percentage)

```python
transformation=[{"width": 400}]
# → tr=w-400
```

```python
transformation=[{"width": 0.5}]
# → tr=w-0.5   (50% of original)
```

### `w-auto`

```python
transformation=[{"width": "auto"}]
# → tr=w-auto
```

---

### `h` — height

```python
transformation=[{"height": 300}]
# → tr=h-300
```

```python
transformation=[{"height": 0.25}]
# → tr=h-0.25
```

---

## 2. Aspect Ratio

### `ar-<w>-<h>`

```python
transformation=[{"aspect_ratio": "16-9"}]
# → tr=ar-16-9
```

### `ar-<expression>`

```python
transformation=[
    {
        "width": 400,
        "aspect_ratio": "idu_div_2",
    }
]
# → tr=w-400,ar-idu_div_2
```

---

## 3. Crop Modes

### `cm-pad_resize`

```python
transformation=[
    {
        "width": 400,
        "height": 300,
        "crop_mode": "pad_resize",
        "background": "ffffff",
    }
]
# → tr=w-400,h-300,cm-pad_resize,bg-ffffff
```

---

### `c-force`

```python
transformation=[
    {
        "width": 400,
        "height": 300,
        "crop": "force",
    }
]
# → tr=w-400,h-300,c-force
```

---

### `c-at_max`

```python
transformation=[
    {
        "width": 800,
        "height": 600,
        "crop": "at_max",
    }
]
# → tr=w-800,h-600,c-at_max
```

---

### `c-at_max_enlarge`

```python
transformation=[
    {
        "width": 800,
        "height": 600,
        "crop": "at_max_enlarge",
    }
]
# → tr=w-800,h-600,c-at_max_enlarge
```

---

### `c-at_least`

```python
transformation=[
    {
        "width": 800,
        "height": 600,
        "crop": "at_least",
    }
]
# → tr=w-800,h-600,c-at_least
```

---

### `c-maintain_ratio` (default)

```python
transformation=[
    {
        "width": 400,
        "height": 300,
        "crop": "maintain_ratio",
    }
]
# → tr=w-400,h-300,c-maintain_ratio
```

---

## 4. Extract / Pad Extract

### `cm-extract`

```python
transformation=[
    {
        "width": 200,
        "height": 200,
        "crop_mode": "extract",
        "x": 100,
        "y": 50,
    }
]
# → tr=w-200,h-200,cm-extract,x-100,y-50
```

---

### `cm-pad_extract`

```python
transformation=[
    {
        "width": 200,
        "height": 200,
        "crop_mode": "pad_extract",
        "background": "000000",
    }
]
# → tr=w-200,h-200,cm-pad_extract,bg-000000
```

---

## 5. Focus (`fo-*`)

### Alignment (pad resize)

```python
transformation=[
    {
        "width": 400,
        "height": 300,
        "crop_mode": "pad_resize",
        "focus": "left",
    }
]
# → tr=w-400,h-300,cm-pad_resize,fo-left
```

Other valid values:

```
This parameter can have the following values depending on where it is being used:

left, right, top, bottom with pad resize

fo-custom with maintain ratio and extract crop.

center, top, left, bottom, right, top_left, top_right, bottom_left and bottom_right can be used to define relative cropping during extract crop.
```

---

### Extract focus positions

```python
transformation=[
    {
        "width": 200,
        "height": 200,
        "crop_mode": "extract",
        "focus": "top_left",
    }
]
# → tr=w-200,h-200,cm-extract,fo-top_left
```

---

### Smart / AI focus

```python
transformation=[{"focus": "auto"}]
# → tr=fo-auto
```

```python
transformation=[{"focus": "face"}]
# → tr=fo-face
```

---

### Object-aware focus

```python
transformation=[{"focus": "car"}]
# → tr=fo-car
```

```python
transformation=[{"focus": "person_dog"}]
# → tr=fo-person_dog
```

---

## 6. Coordinates

### `x`, `y`

```python
transformation=[
    {
        "crop_mode": "extract",
        "x": 120,
        "y": 80,
    }
]
# → tr=cm-extract,x-120,y-80
```

### `xc`, `yc`

```python
transformation=[
    {
        "crop_mode": "extract",
        "xc": 300,
        "yc": 200,
    }
]
# → tr=cm-extract,xc-300,yc-200
```

---

## 7. Zoom

```python
transformation=[
    {
        "focus": "face",
        "zoom": 1.5,
    }
]
# → tr=fo-face,z-1.5
```

---

## 8. DPR

### Explicit DPR

```python
transformation=[{"dpr": 2}]
# → tr=dpr-2
```

### `dpr-auto`

```python
transformation=[{"dpr": "auto"}]
# → tr=dpr-auto
```

---

## 9. Arithmetic Expressions (Example)

```python
transformation=[
    {
        "width": "idu_div_2",
        "height": "idu_mul_0.25",
    }
]
# → tr=w-idu_div_2,h-idu_mul_0.25
```

---

## Key Takeaways (important for your Strands tool)

1. **No-value transforms are enums**, not booleans
   (`"crop": "force"`, not `True`)

2. **Everything maps cleanly to strings**
   → perfect for LLM-generated structured output

3. **Your `SUPPORTED_TRANSFORMS` file is sufficient**
   to deterministically build URLs without doc lookup

---

If you want next:

* ✅ Auto-generate these examples from your mapping
* ✅ Convert this into a **machine-readable schema for LLMs**
* ✅ Validation rules per transform
* ✅ Conflict resolution logic (`w + h + ar`, etc.)

Just tell me the next step.

---

| transformation_parameter | transformation_param_value_type | limitation_if_any                                                               | description                                                      | used_in                      |
| ------------------------ | ------------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------- |
| `w`                      | number                          | `> 1` absolute px OR `0 < value ≤ 1` as percentage; max implied by image limits | Sets output image width; auto-scales height if `h` not specified | image, arithmetic_expression |
| `w-auto`                 | no_value                        | Requires `Sec-CH-Width` client hint                                             | Automatically derives width from client hint header              | image                        |
| `h`                      | number                          | `> 1` absolute px OR `0 < value ≤ 1` as percentage                              | Sets output image height; auto-scales width if `w` not specified | image, arithmetic_expression |
| `ar-<w>-<h>`             | number                          | Ignored if both `w` and `h` are specified                                       | Sets aspect ratio of output image                                | image                        |
| `ar-<expression>`        | number                          | Must be used with `w` or `h`                                                    | Aspect ratio derived via arithmetic expression                   | image, arithmetic_expression |
| `cm-pad_resize`          | no_value                        | Requires both `w` and `h`                                                       | Preserves image, adds padding to match exact dimensions          | image                        |
| `c-force`                | no_value                        | Requires both `w` and `h`                                                       | Forces image to exact dimensions without preserving aspect ratio | image                        |
| `c-at_max`               | no_value                        | Does not enlarge beyond original dimensions                                     | Preserves image, resizes to max container size                   | image                        |
| `c-at_max_enlarge`       | no_value                        | None                                                                            | Same as `c-at_max` but allows upscaling                          | image                        |
| `c-at_least`             | no_value                        | None                                                                            | Ensures output is at least requested size                        | image                        |
| `c-maintain_ratio`       | no_value                        | Default crop strategy                                                           | Crops while preserving aspect ratio                              | image                        |
| `cm-extract`             | no_value                        | Crop fails if extraction exceeds image bounds                                   | Extracts fixed-size region from image                            | image                        |
| `cm-pad_extract`         | no_value                        | Requires `bg` for visible padding                                               | Extracts region, pads if image is smaller                        | image                        |
| `fo-left`                | no_value                        | Used with pad resize                                                            | Aligns image left, pads right                                    | image                        |
| `fo-right`               | no_value                        | Used with pad resize                                                            | Aligns image right, pads left                                    | image                        |
| `fo-top`                 | no_value                        | Used with pad resize                                                            | Aligns image top, pads bottom                                    | image                        |
| `fo-bottom`              | no_value                        | Used with pad resize                                                            | Aligns image bottom, pads top                                    | image                        |
| `fo-center`              | no_value                        | Default for extract                                                             | Extracts from center                                             | image                        |
| `fo-top_left`            | no_value                        | Extract mode only                                                               | Relative extract position                                        | image                        |
| `fo-top_right`           | no_value                        | Extract mode only                                                               | Relative extract position                                        | image                        |
| `fo-bottom_left`         | no_value                        | Extract mode only                                                               | Relative extract position                                        | image                        |
| `fo-bottom_right`        | no_value                        | Extract mode only                                                               | Relative extract position                                        | image                        |
| `fo-custom`              | no_value                        | Requires custom focus metadata                                                  | Uses predefined focus area                                       | image                        |
| `fo-auto`                | no_value                        | Accuracy not guaranteed                                                         | Smart auto-detection of important region                         | image                        |
| `fo-face`                | no_value                        | Works best with faces                                                           | Detects and focuses on faces                                     | image                        |
| `fo-<object>`            | no_value                        | Object must be in supported COCO list                                           | Object-aware cropping                                            | image                        |
| `fo-<obj1>_<obj2>`       | no_value                        | Uses first detected object                                                      | Multi-object fallback focus                                      | image                        |
| `x`                      | number                          | Used only with `cm-extract`                                                     | X coordinate of top-left crop                                    | image, arithmetic_expression |
| `y`                      | number                          | Used only with `cm-extract`                                                     | Y coordinate of top-left crop                                    | image, arithmetic_expression |
| `xc`                     | number                          | Crop fails if bounds exceed image                                               | X coordinate of crop center                                      | image, arithmetic_expression |
| `yc`                     | number                          | Crop fails if bounds exceed image                                               | Y coordinate of crop center                                      | image, arithmetic_expression |
| `z`                      | number                          | Must be used with `fo-face` or `fo-object`                                      | Controls zoom in/out during object crop                          | image                        |
| `dpr`                    | number                          | Effective only if final size is `1px–5000px`                                    | Device Pixel Ratio scaling                                       | image                        |
| `dpr-auto`               | no_value                        | Requires `Sec-CH-DPR` header                                                    | Auto DPR from client hints                                       | image                        |


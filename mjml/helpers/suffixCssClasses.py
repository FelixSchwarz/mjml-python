
__all__ = ['suffixCssClasses']

def suffixCssClasses(classes, suffix):
    if not classes:
        return ''
    class_list = classes.split(' ')
    suffixed_classes = map(lambda cls_str: f'{cls_str}-{suffix}', class_list)
    return ' '.join(suffixed_classes)

